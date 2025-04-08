# Upwork Job Discord Bot

A Discord bot that automatically scrapes Upwork jobs and posts them to appropriate channels based on job categories.

## Features

- Automatically scrapes Upwork jobs at regular intervals
- Categorizes jobs into different channels (frontend, backend, fullstack, automation, scraping, other)
- Filters out unwanted job categories (AI, data science, game development, DevOps)
- Provides interactive buttons to show full job descriptions
- Includes commands for manual job checking and filtering

## Setup

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file with the following variables:
   ```
   DISCORD_TOKEN=your_discord_bot_token
   FRONTEND_CHANNEL_ID=channel_id
   BACKEND_CHANNEL_ID=channel_id
   FULLSTACK_CHANNEL_ID=channel_id
   AUTOMATION_CHANNEL_ID=channel_id
   SCRAPING_CHANNEL_ID=channel_id
   OTHER_CHANNEL_ID=channel_id
   ```
4. Run the bot:
   ```
   python discord_bot.py
   ```

## Commands

- `!check` - Manually check for new jobs
- `!status` - Check bot status and channel configuration
- `!filter <job_id>` - Manually filter a job by ID
- `!filtered` - List all manually filtered job IDs

## Project Structure

- `discord_bot.py` - Main bot file with Discord commands and event handlers
- `job_scraper.py` - Module for scraping Upwork jobs
- `job_categorizer.py` - Module for categorizing jobs
- `config.py` - Configuration settings and constants
- `requirements.txt` - Python dependencies
- `.env` - Environment variables (not included in repository)

## Customization

You can customize the job categories and keywords in `config.py`:

- `JOB_CATEGORIES` - Define job categories and their keywords
- `FILTERED_TERMS` - Define terms to filter out
- `CHECK_INTERVAL` - Set the interval for checking new jobs (in seconds)

## License

MIT
