import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Keys
FIRECRAWL_API_KEY = os.getenv('FIRECRAWL_API_KEY')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# App Configuration
APP_TITLE = "AI-Powered Topic Optimizer"
APP_DESCRIPTION = "Elevate your content's AI readiness."

# Crawling Configuration
MAX_PAGES_DEFAULT = 5
MAX_PAGES_LIMIT = 50

# Analysis Configuration
CONTENT_MAX_LENGTH = 8000  # Max content length for analysis
GEMINI_MODEL = "gemini-pro"

# UI Configuration
THEME_COLORS = {
    'primary': '#ff8c42',
    'secondary': '#8b9dc3', 
    'tertiary': '#313856',
    'background': 'linear-gradient(to bottom right, #1e293b, #374151, #313856)',
    'text': '#f1f5f9',
    'muted': '#94a3b8'
}

# Check if required API keys are set
def check_api_keys():
    """Check if required API keys are configured"""
    missing_keys = []
    
    if not FIRECRAWL_API_KEY:
        missing_keys.append('FIRECRAWL_API_KEY')
    if not GEMINI_API_KEY:
        missing_keys.append('GEMINI_API_KEY')
    
    return missing_keys 