import cloudscraper
from bs4 import BeautifulSoup
import logging
import asyncio
import re
import random
from config import UPWORK_URL, MAX_RETRIES, RETRY_DELAY
from utils import restart_warp  # Import restart_warp from utils.py

logger = logging.getLogger("upwork_bot")

class UpworkScraper:
    def __init__(self):
        self.scraper = cloudscraper.create_scraper()
        self.last_job_title = None
        self.first_run = True
        self.job_descriptions = {}
        self.filtered_jobs = set()
        self.message_job_map = {}

    async def fetch_jobs(self):
        """Fetch job listings from Upwork search results page"""
        try:
            logger.info("Fetching job list from Upwork...")
            response = self.scraper.get(UPWORK_URL)
            
            # Check for 403 error and restart WARP if needed
            if response.status_code == 403:
                logger.warning("Received 403 Forbidden error. Restarting WARP...")
                restart_warp()
                # Retry the request after restarting WARP
                response = self.scraper.get(UPWORK_URL)
            
            html = response.text
            soup = BeautifulSoup(html, "html.parser")
            
            job_elements = soup.find_all('h2', class_='h5 mb-0 mr-2 job-tile-title')
            if not job_elements:
                logger.error("No job elements found on the page")
                return []
            
            logger.info(f"Found {len(job_elements)} jobs on the page")
            
            jobs = []
            newest_job_title = job_elements[0].text.strip()
            logger.info(f"Newest job title: {newest_job_title}")
            
            # If this is the first run, process the top 5 jobs
            limit = 5 if self.first_run else len(job_elements)
            count = 0
            
            for job_element in job_elements:
                if self.first_run and count >= limit:
                    logger.info("First run limit reached")
                    break
                    
                a_tag = job_element.find('a')
                if not a_tag:
                    continue
                    
                title = a_tag.text.strip()
                
                # Skip if we've seen this job before and it's not the first run
                if not self.first_run and title == self.last_job_title:
                    logger.info(f"Reached previously seen job: {title}")
                    break
                
                job_link = 'https://upwork.com' + a_tag['href']
                logger.info(f"Processing job: {title}")
                
                try:
                    job_data = await self._fetch_and_extract_job_details(job_link, title)
                    if job_data:
                        jobs.append(job_data)
                        count += 1
                        await asyncio.sleep(1)  # Small delay between jobs
                except Exception as e:
                    logger.error(f"Error processing job {title}: {e}")
                    continue
            
            if jobs:
                self.last_job_title = newest_job_title
                logger.info(f"Updated last job title to: {self.last_job_title}")
            
            if self.first_run:
                self.first_run = False
                logger.info("First run completed")
            
            return jobs
            
        except Exception as e:
            logger.error(f"Error in fetch_jobs: {e}")
            return []

    async def _fetch_and_extract_job_details(self, job_url, title):
        """Fetch and extract job details using the working version's logic"""
        try:
            logger.info(f"Fetching details for: {job_url}")
            response = self.scraper.get(job_url)
            print(response.status_code)
            
            # Check for 403 error and restart WARP if needed
            if response.status_code == 403:
                logger.warning("Received 403 Forbidden error. Restarting WARP...")
                restart_warp()
                # Retry the request after restarting WARP
                response = self.scraper.get(job_url)
            
            html = response.text
            soup = BeautifulSoup(html, "html.parser")
            
            # Extract description
            text_element = soup.find('div', class_='break mt-2')
            description = text_element.text if text_element else "Description not available"
            # Keep description formatting by not removing whitespace
            # description = re.sub(r'\s+', ' ', description).strip()
            
            # Extract price
            price = "Not specified"
            price_elements = soup.find_all(class_='description')
            if price_elements and len(price_elements) > 0:
                price_element = price_elements[0].find_previous_sibling()
                if price_element:
                    price = price_element.get_text(strip=True)
                    if price[0] != "$" and len(price_elements) > 3:
                        price_element = price_elements[3].find_previous_sibling()
                        if price_element:
                            price = price_element.get_text(strip=True)
                        if price == "Ongoing project" or price == "Complex project":
                            price = "Not Sure"
            
            # Extract proposals
            proposal_element = soup.find(class_='value')
            proposal = proposal_element.text if proposal_element else "Not specified"
            
            # Store description for later use
            self.job_descriptions[job_url] = description
            
            return (job_url, title, description, job_url, proposal, price)
            
        except Exception as e:
            logger.error(f"Error fetching details for {title}: {e}")
            return None

    def update_last_job(self, job_title):
        """Update the last job title marker"""
        self.last_job_title = job_title
        logger.info(f"Updated last job title to: {job_title}")

    def complete_first_run(self):
        """Mark first run as complete"""
        if self.first_run:
            self.first_run = False
            logger.info("First run completed")

    def add_filtered_job(self, job_id):
        """Add a job ID to the filtered list"""
        self.filtered_jobs.add(job_id)
        logger.info(f"Added job {job_id} to filtered list")

    def get_job_description(self, job_id):
        """Get the description for a job ID"""
        return self.job_descriptions.get(job_id)

    def get_job_activity(self, job_url):
        """Get the activity data (proposals, etc.) for a job"""
        try:
            # If we don't have HTML for this job, fetch it
            response = self.scraper.get(job_url)
            html = response.text
            soup = BeautifulSoup(html, "html.parser")
            
            # Extract the Activity section
            activity_section = soup.find('section', class_='air3-card-section py-4x')
            
            if not activity_section:
                return None
                
            # Extract all activity items
            activity_data = []
            
            # Extract proposals
            proposals_item = activity_section.find('li', class_='ca-item')
            if proposals_item:
                title_span = proposals_item.find('span', class_='title')
                value_span = proposals_item.find('span', class_='value')
                if title_span and value_span:
                    proposals_text = f"{title_span.text.strip()} {value_span.text.strip()}"
                    activity_data.append(proposals_text)
            
            # Extract other items (interviewing, invites, etc.)
            other_items = activity_section.find_all('li', class_='ca-item')
            for item in other_items[1:] if other_items else []:
                title_span = item.find('span', class_='title')
                value_div = item.find('div', class_='value')
                if title_span and value_div:
                    item_text = f"{title_span.text.strip()} {value_div.text.strip()}"
                    activity_data.append(item_text)
            
            # Join all activity data into one string
            if activity_data:
                return "\n".join(activity_data)
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error getting activity data for {job_url}: {e}")
            return None 