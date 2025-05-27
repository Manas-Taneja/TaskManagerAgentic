# ai_task_manager/config.py
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database settings
DB_PATH = os.getenv("DB_PATH", "ai_task_manager.db")

# Search API settings
SERPAPI_KEY = os.getenv("SERPAPI_KEY")

# LLM API settings
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Email settings
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_USERNAME = os.getenv("EMAIL_USERNAME")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECIPIENT = os.getenv("EMAIL_RECIPIENT")

# Application settings
DEFAULT_TASK_PRIORITY = 1
DEFAULT_TASK_STATUS = "pending"
MAX_SEARCH_RESULTS = 5
DAYS_BETWEEN_UPDATES = 1