import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncio
import sys
import time
from discord.ui import Button, View
import logging

from config import TOKEN, CHANNEL_IDS, JOB_CATEGORIES, COMMAND_PREFIX
from job_scraper import UpworkScraper
from job_categorizer import JobCategorizer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("upwork_bot")

# Set the event loop policy for Windows
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Load environment variables
load_dotenv()

# Initialize bot with all necessary intents
intents = discord.Intents.all()  # Enable all intents
bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)

# Initialize job scraper
job_scraper = UpworkScraper()

# Variable to track the latest job
old_job = None
# Flag to track if this is the first run
first_run = True

# Helper function to create the initial job embed
def create_job_embed(job_category, job_data):
    job_id, title, description, link, proposal, price = job_data
    emoji = JOB_CATEGORIES[job_category]['emoji']
    
    embed = discord.Embed(
        title=f"{emoji} {title}", 
        url=link, 
        color=discord.Color.blue() # Or choose a color you like
    )
    embed.add_field(name="Price", value=price if price else "N/A", inline=True)
    embed.add_field(name="Proposals", value=proposal if proposal else "N/A", inline=True)
    # We don't add the description here initially
    embed.set_footer(text=f"Job ID: {job_id}")
    return embed

# View class for the "Show More" button
class JobView(View):
    def __init__(self, job_id):
        super().__init__(timeout=None) # Persist view across bot restarts (optional)
        self.job_id = job_id
        # Create a shorter custom ID using a hash of the job URL
        short_id = str(hash(job_id) % 1000000)  # Convert to a 6-digit number
        self.add_item(Button(label="Show More", style=discord.ButtonStyle.primary, custom_id=f"show_{short_id}"))

async def send_discord_message(job_category, job_data):
    job_id, title, description, link, proposal, price = job_data
    try:
        channel_id = CHANNEL_IDS.get(job_category)
        if not channel_id:
            logger.warning(f"No channel ID found for category: {job_category}")
            return

        channel = bot.get_channel(channel_id)
        if not channel:
            logger.warning(f"Could not find channel with ID: {channel_id}")
            return

        logger.info(f"Preparing job for channel: {channel.name} (ID: {channel.id}) - Job ID: {job_id}")
        
        # Create the initial embed and view
        embed = create_job_embed(job_category, job_data)
        view = JobView(job_id)
        
        # Add retry logic for sending messages
        max_retries = 3
        retry_count = 0
        success = False
        
        while retry_count < max_retries and not success:
            try:
                await channel.send(embed=embed, view=view)
                logger.info(f"Successfully sent job {job_id} to {job_category} channel: {title}")
                success = True
            except discord.errors.RateLimited as e:
                retry_after = e.retry_after
                logger.warning(f"Rate limited sending job {job_id}. Waiting {retry_after:.2f} seconds...")
                await asyncio.sleep(retry_after)
                retry_count += 1
            except Exception as e:
                logger.error(f"Failed to send job {job_id} (attempt {retry_count + 1}/{max_retries}): {e}")
                retry_count += 1
                await asyncio.sleep(5)  # Wait before retrying
        
        if not success:
            logger.error(f"Failed to send job {job_id} after {max_retries} attempts: {title}")

    except Exception as e:
        logger.error(f"Error in send_discord_message for job {job_id}: {e}")
        import traceback
        traceback.print_exc()

async def check_upwork_jobs():
    """Check for new Upwork jobs and send them to Discord"""
    try:
        # Fetch jobs from Upwork
        jobs = await job_scraper.fetch_jobs()
        
        if not jobs:
            logger.info("No jobs found. Retrying in next cycle.")
            return
        
        new_jobs_found = False
        newest_job_title = None
        
        # Process each job
        for job_data in jobs:
            try:
                job_id, title, description, link, proposal, price = job_data
                
                # Skip if job should be filtered based on keywords
                if JobCategorizer.is_filtered_job(title, description):
                    logger.info(f"Filtered job by content: {title} ({job_id})")
                    job_scraper.add_filtered_job(job_id)
                    continue
                
                # Get job categories
                categories = JobCategorizer.get_job_category(title, description)
                
                logger.info(f"Processing job: {title} ({job_id}) for categories: {categories}")
                
                # Send to appropriate channels
                for category in categories:
                    if category in CHANNEL_IDS:
                        await send_discord_message(category, job_data)
                
                new_jobs_found = True
                if newest_job_title is None:
                    newest_job_title = title
                
            except Exception as e:
                # Log error with job_id if available
                job_id_str = f" (Job ID: {job_id})" if 'job_id' in locals() else ""
                logger.error(f"Error processing job{job_id_str}: {e}")
                import traceback
                traceback.print_exc() # Print full traceback for debugging
                continue
        
        # Update last job with the title of the newest job processed in this cycle
        if new_jobs_found and newest_job_title:
            job_scraper.update_last_job(newest_job_title)
        
        if job_scraper.first_run:
            job_scraper.complete_first_run()
        
    except Exception as e:
        logger.error(f"Major error in check_upwork_jobs loop: {e}")
        import traceback
        traceback.print_exc() # Print full traceback for debugging

@bot.event
async def on_ready():
    logger.info(f'{bot.user} has connected to Discord!')
    logger.info(f'Bot is in {len(bot.guilds)} servers')
    for guild in bot.guilds:
        logger.info(f'- {guild.name} (ID: {guild.id})')
        for channel in guild.text_channels:
            logger.info(f'  - {channel.name} (ID: {channel.id})')
    
    logger.info("Looking for channels...")
    for category, channel_id in CHANNEL_IDS.items():
        channel = bot.get_channel(channel_id)
        if channel:
            logger.info(f"Found {category} channel: {channel.name}")
        else:
            logger.warning(f"Could not find {category} channel with ID: {channel_id}")
    
    # Start the job checking loop
    bot.loop.create_task(check_upwork_jobs())
    logger.info("Bot is ready and listening for interactions.")

@bot.event
async def on_interaction(interaction):
    """Handle button interactions"""
    if interaction.type == discord.InteractionType.component:
        if interaction.data['custom_id'].startswith('show_'):
            try:
                # Get the job ID from the custom ID
                short_id = interaction.data['custom_id'].split('_')[1]
                
                # Find the original job URL from the embed
                job_url = None
                for embed in interaction.message.embeds:
                    if embed.footer and embed.footer.text.startswith('Job ID:'):
                        job_url = embed.footer.text.split('Job ID: ')[1]
                        break
                
                if not job_url:
                    await interaction.response.send_message("Could not find job details.", ephemeral=True)
                    return
                
                # Get the description from the scraper
                description = job_scraper.get_job_description(job_url)
                if not description:
                    await interaction.response.send_message("Job description not available.", ephemeral=True)
                    return
                
                # Create a new embed with the full description
                embed = discord.Embed(
                    title=interaction.message.embeds[0].title,
                    description=description,
                    color=discord.Color.blue()
                )
                
                # Add the original fields
                for field in interaction.message.embeds[0].fields:
                    embed.add_field(name=field.name, value=field.value, inline=field.inline)
                
                # Update the message with the full description
                await interaction.response.edit_message(embed=embed, view=None)
                
            except Exception as e:
                logger.error(f"Error handling show more interaction: {e}")
                await interaction.response.send_message("An error occurred while showing the full description.", ephemeral=True)
    else:
        # Handle other types of interactions (like commands)
        await bot.process_commands(interaction)

# Command to manually check for jobs
@bot.command(name='check')
async def check(ctx):
    await ctx.send("Checking for new Upwork jobs...")
    await ctx.message.add_reaction('👍')
    
    # Force a full check
    job_scraper.first_run = True
    
    # Create a separate task for checking jobs to avoid blocking the command
    bot.loop.create_task(check_upwork_jobs())

# Command to check bot status
@bot.command(name='status')
async def status(ctx):
    """Check the bot's status and configuration"""
    try:
        # Get uptime
        uptime = time.time() - bot.start_time
        hours, remainder = divmod(uptime, 3600)
        minutes, seconds = divmod(remainder, 60)
        uptime_str = f"{int(hours)}h {int(minutes)}m {int(seconds)}s"
        
        # Get channel information
        channel_info = []
        for category, channel_id in CHANNEL_IDS.items():
            channel = bot.get_channel(channel_id)
            if channel:
                channel_info.append(f"✅ {category}: #{channel.name}")
            else:
                channel_info.append(f"❌ {category}: Channel not found")
        
        # Create status message
        status_message = f"**Bot Status**\n"
        status_message += f"Uptime: {uptime_str}\n"
        status_message += f"Last job check: {job_scraper.last_job if job_scraper.last_job else 'None'}\n\n"
        status_message += "**Channel Configuration**\n"
        status_message += "\n".join(channel_info)
        
        await ctx.send(status_message)
    except Exception as e:
        await ctx.send(f"Error checking status: {e}")

# Add start_time to track uptime
bot.start_time = time.time()

# Command to manually filter a job
@bot.command(name='filter')
async def filter_job(ctx, job_id=None):
    """Manually filter a job by ID"""
    if not job_id:
        await ctx.send("Please provide a job ID to filter. Usage: !filter <job_id>")
        return
    
    try:
        # Extract job ID from the provided string
        job_id = job_id.strip()
        if not job_id.isdigit():
            await ctx.send("Invalid job ID. Please provide a numeric ID.")
            return
        
        # Add the job ID to the filtered jobs list
        job_scraper.add_filtered_job(job_id)
        await ctx.send(f"Job ID {job_id} has been added to the filter list.")
    except Exception as e:
        await ctx.send(f"Error filtering job: {e}")

# Command to list filtered jobs
@bot.command(name='filtered')
async def list_filtered(ctx):
    """List all manually filtered job IDs"""
    if not job_scraper.filtered_jobs:
        await ctx.send("No jobs have been manually filtered.")
        return
    
    # Create a message with all filtered job IDs
    filtered_list = "\n".join([f"- {job_id}" for job_id in sorted(job_scraper.filtered_jobs)])
    await ctx.send(f"**Manually Filtered Jobs**\n{filtered_list}")

# Run the bot
bot.run(TOKEN) 