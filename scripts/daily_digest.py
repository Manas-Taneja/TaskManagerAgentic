# scripts/daily_digest.py
import os
import sys
import logging
from dotenv import load_dotenv

# Add parent directory to path to import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai_task_manager.database import TaskDatabase
from ai_task_manager.search_service import SearchService
from ai_task_manager.llm_service import LLMService
from ai_task_manager.email_service import EmailService
from ai_task_manager.task_manager import TaskManager

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("daily_digest.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Generate and send daily digest email."""
    try:
        # Initialize services
        db = TaskDatabase()
        search_service = SearchService()
        llm_service = LLMService()
        email_service = EmailService()
        task_manager = TaskManager(db, search_service, llm_service)
        
        # First, update all tasks that need new insights
        logger.info("Updating tasks...")
        updated_tasks = task_manager.update_all_tasks()
        logger.info(f"Updated {len(updated_tasks)} tasks")
        
        # Generate the daily digest
        logger.info("Generating daily digest...")
        digest_content = task_manager.generate_daily_digest()
        
        # Send the digest email
        logger.info("Sending digest email...")
        success = email_service.send_daily_digest(digest_content)
        
        if success:
            logger.info("Daily digest sent successfully")
        else:
            logger.error("Failed to send daily digest email")
            sys.exit(1)
    
    except Exception as e:
        logger.error(f"Error running daily digest: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()