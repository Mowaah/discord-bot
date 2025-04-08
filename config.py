import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot configuration
TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_IDS = {
    'frontend': int(os.getenv('FRONTEND_CHANNEL_ID')),
    'backend': int(os.getenv('BACKEND_CHANNEL_ID')),
    'fullstack': int(os.getenv('FULLSTACK_CHANNEL_ID')),
    'automation': int(os.getenv('AUTOMATION_CHANNEL_ID')),
    'scraping': int(os.getenv('SCRAPING_CHANNEL_ID')),
    'other': int(os.getenv('OTHER_CHANNEL_ID'))
}
# Upwork configuration
UPWORK_URL = "https://www.upwork.com/nx/search/jobs/?page=1&per_page=20&q=%28frontend%20OR%20backend%20OR%20%22full%20stack%22%20OR%20scraping%20OR%20scrapping%20OR%20automation%20OR%20automations%29&sort=recency"

# Job category emojis and keywords
JOB_CATEGORIES = {
    'frontend': {
        'emoji': '🎨',
        'keywords': [
            # Core web technologies
            'html5', 'css3', 'javascript', 'typescript',
            
            # React ecosystem
            'react', 'next.js', 'nextjs', 'react native', 'redux', 'context api',
            'react navigation', 'react native paper',
            
            # UI frameworks and libraries
            'tailwind', 'tailwindcss', 'sass', 'scss', 'material ui', 'mui',
            'shadcn', 'shadcn/ui', 'responsive design', 'mobile development',
            
            # Storage and data
            'asyncstorage', 'local storage', 'session storage',
            
            # API and data fetching
            'rest api', 'graphql', 'fetch', 'axios',
            
            # Version control
            'git', 'github', 'gitlab', 'bitbucket',
            
            # General frontend terms
            'frontend', 'ui', 'ux', 'web design', 'web development',
            'front-end', 'front end', 'responsive', 'mobile-first', 'mobile first',
            'ui/ux', 'ui design', 'ux design', 'user interface', 'landing page',
            'web app', 'web application', 'single page application', 'spa',
            'progressive web app', 'pwa', 'web accessibility', 'a11y'
        ]
    },
    'backend': {
        'emoji': '⚙️',
        'keywords': [
            'backend', 'api', 'server', 'database', 'node', 'python', 'java', 'php', 'ruby',
            'django', 'flask', 'express', 'spring', 'spring boot', 'laravel', 'rails',
            'graphql', 'rest api', 'restful', 'microservices', 'serverless', 'lambda',
            'postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch', 'dynamodb',
            'sql', 'nosql', 'orm', 'jpa', 'hibernate', 'prisma', 'sequelize',
            'authentication', 'authorization', 'jwt', 'oauth', 'oauth2', 'openid',
            'websocket', 'socket.io', 'grpc', 'backend developer', 'backend development',
            'backend engineer', 'backend engineering', 'api development', 'api design',
            'database design', 'database administration', 'dba', 'data modeling',
            'backend architecture', 'system design', 'scalability', 'performance optimization'
        ]
    },
    'fullstack': {
        'emoji': '🏗️',
        'keywords': ['full stack', 'fullstack', 'full-stack', 'full stack developer', 'wordpress', 'web application']
    },
    'automation': {
        'emoji': '🤖',
        'keywords': ['automation', 'automated', 'automate', 'bot', 'script', 'workflow automation', 'process automation']
    },
    'scraping': {
        'emoji': '🔍',
        'keywords': ['scraping', 'scrapper', 'scraper', 'data extraction', 'web scraping']
    },
    'other': {
        'emoji': '💻',
        'keywords': []  # Empty keywords list means it will catch anything not categorized
    }
}

# AI-related terms to filter out
FILTERED_TERMS = {
    'ai': [
        'artificial intelligence', 'machine learning', 'deep learning', 
        'neural network','llm', 'large language model', 'prompt engineering',
        'prompt engineer', 'ai engineer', 'ai developer', 'ai integration'
    ],
    'data': [
        'data science', 'data scientist', 'data analysis', 'data analytics',
        'data engineer', 'data engineering', 'data mining', 'data warehouse',
        'business intelligence', 'power bi', 'tableau', 'statistics',
        'big data', 'data lake', 'etl', 'data pipeline', 'data modeling',
        'data visualization', 'predictive analytics', 'data processing'
    ],
    'game': [
        'game development', 'game dev', 'game programming', 'game designer',
        'unity', 'unreal engine', 'game engine', 'gaming', 'game mechanics',
        'game physics', '3d game', '2d game', 'mobile game', 'video game',
        'multiplayer game', 'game server', 'game client', 'game backend'
    ],
    'devops': [
        'devops', 'aws', 'azure', 'gcp', 'google cloud', 'cloud computing',
        'cloud architect', 'cloud infrastructure', 'cloud native', 'kubernetes',
        'docker', 'containerization', 'ci/cd', 'jenkins', 'terraform',
        'infrastructure as code', 'iac', 'ansible', 'puppet', 'chef',
        'microservices', 'service mesh', 'cloud migration', 'cloud security',
        'devsecops', 'site reliability', 'sre', 'platform engineer',
        'gitlab', 'bitbucket', 'circleci', 'travis'
    ]
}

# Bot settings
COMMAND_PREFIX = '!'
CHECK_INTERVAL = 120 # 5 minutes in seconds
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds 