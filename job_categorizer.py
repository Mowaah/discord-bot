import re
import logging
from config import JOB_CATEGORIES, FILTERED_TERMS

logger = logging.getLogger("upwork_bot")

# Constants for scoring weights
TITLE_EXACT_MATCH_WEIGHT = 10
TITLE_KEYWORD_WEIGHT = 5
DESCRIPTION_KEYWORD_WEIGHT = 1
FULLSTACK_TITLE_BOOST = 3 # Additional boost if 'fullstack' in title
JS_TITLE_BOOST = 3        # Additional boost if 'javascript' in title

class JobCategorizer:
    @staticmethod
    def get_job_category(job_title, job_description):
        """Determine the job categories based on title and description keywords with refined scoring"""
        title_lower = job_title.lower()
        text_to_check = (title_lower + " " + job_description).lower()
        
        # Count keyword matches for each category
        category_scores = {category: 0 for category in JOB_CATEGORIES}
        
        # --- Scoring Logic --- 
        for category, info in JOB_CATEGORIES.items():
            if category == 'other': continue
            
            for keyword in info['keywords']:
                keyword_lower = keyword.lower()
                # Higher score for keywords found in the title
                if keyword_lower in title_lower:
                    category_scores[category] += TITLE_KEYWORD_WEIGHT
                    # Bonus for exact title match (or close match)
                    if keyword_lower == title_lower: # Simplistic exact match check
                        category_scores[category] += TITLE_EXACT_MATCH_WEIGHT
                        
                # Lower score for keywords found only in the description
                elif keyword_lower in text_to_check:
                    category_scores[category] += DESCRIPTION_KEYWORD_WEIGHT

        # Apply boosts based on specific title keywords
        if 'fullstack' in title_lower or 'full stack' in title_lower or 'full-stack' in title_lower:
            category_scores['fullstack'] += FULLSTACK_TITLE_BOOST
        if 'javascript' in title_lower:
             category_scores['frontend'] += JS_TITLE_BOOST

        # --- Categorization Logic --- 
        categories = []
        
        # Special case: Scraping & Automation often overlap
        if category_scores['scraping'] > 0 and category_scores['automation'] > 0:
            # If both have significant scores, assign both
            # You might adjust the threshold (e.g., > TITLE_KEYWORD_WEIGHT)
            categories.append('scraping')
            categories.append('automation')
            # Optionally remove them from consideration for other categories if desired
            # del category_scores['scraping']
            # del category_scores['automation']
            # return categories # Decide if this combination is exclusive

        # Refined Fullstack Logic:
        # Requires a decent score AND presence of frontend/backend keywords unless score is very high
        min_fullstack_score_for_override = TITLE_KEYWORD_WEIGHT + FULLSTACK_TITLE_BOOST
        if category_scores['fullstack'] >= min_fullstack_score_for_override:
            has_frontend_keywords = category_scores['frontend'] > 0
            has_backend_keywords = category_scores['backend'] > 0
            # Prioritize fullstack if it has frontend/backend elements OR if its score is dominant
            is_dominant = category_scores['fullstack'] > (category_scores['frontend'] + category_scores['backend']) # Example dominance check
            if (has_frontend_keywords and has_backend_keywords) or is_dominant:
                 # Check if frontend/backend scores are not significantly higher
                 if not (category_scores['frontend'] > category_scores['fullstack'] * 1.5 or 
                         category_scores['backend'] > category_scores['fullstack'] * 1.5):
                     return ['fullstack'] # Assign only fullstack

        # JavaScript job special case (often frontend)
        min_js_score = TITLE_KEYWORD_WEIGHT + JS_TITLE_BOOST
        if category_scores['frontend'] >= min_js_score and 'javascript' in text_to_check:
             # If frontend score is high due to JS, and fullstack score isn't dominant
             if category_scores['fullstack'] < category_scores['frontend']:
                 return ['frontend']

        # General Case: Find the highest scoring category(ies)
        if not categories: # If not already assigned by special cases
             # Remove 'other' for max score calculation
             scores_without_other = {cat: score for cat, score in category_scores.items() if cat != 'other'}
             
             if not scores_without_other or max(scores_without_other.values()) == 0:
                 return ['other']
                 
             max_score = max(scores_without_other.values())
             
             # Determine a threshold for significance (e.g., must be at least title keyword weight)
             significance_threshold = TITLE_KEYWORD_WEIGHT 
             if max_score < significance_threshold:
                 return ['other']

             # Collect all categories matching the max score
             for category, score in scores_without_other.items():
                 if score == max_score:
                     categories.append(category)

             # If multiple categories tie for max score, consider returning 'other' or all tied categories
             # For now, returning all tied categories
             if categories:
                 return categories

        # Fallback to 'other' if no other category assigned
        return categories if categories else ['other']

    @staticmethod
    def is_filtered_job(job_title, job_description):
        """Check if a job should be filtered out based on title and description keywords"""
        title_lower = job_title.lower()
        text_to_check = (title_lower + " " + job_description).lower()
        
        # Check for standalone "AI" (not part of another word)
        if re.search(r'\bai\b', text_to_check):
            logger.info(f"Filtered out AI-related job: {job_title} (matched term: AI)")
            return True

        # Check for exact matches of filtered terms using word boundaries
        for category, terms in FILTERED_TERMS.items():
            for term in terms:
                # Use word boundary to ensure we're matching whole words/phrases
                # Escape special regex characters in the term
                pattern = r'\b' + re.escape(term.lower()) + r'\b'
                if re.search(pattern, text_to_check):
                    logger.info(f"Filtered out {category}-related job: {job_title} (matched term: {term})")
                    return True
        
        return False 