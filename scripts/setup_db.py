# scripts/setup_db.py
import os
import sys
import logging
from dotenv import load_dotenv

# Add parent directory to path to import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai_task_manager.database import TaskDatabase

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def main():
    """Set up the database and create sample tasks if requested."""
    try:
        # Initialize database
        db_path = os.getenv("DB_PATH", "ai_task_manager.db")
        logger.info(f"Setting up database at {db_path}")
        
        db = TaskDatabase(db_path)
        
        # Check if we should add sample tasks
        if "--with-samples" in sys.argv:
            logger.info("Adding sample tasks...")
            
            # Add sample tasks
            task1_id = db.create_task(
                "Research Python async programming",
                "Learn about asyncio, event loops, and async/await syntax for an upcoming project",
                "pending",
                3,
                None
            )
            
            task2_id = db.create_task(
                "Refactor database module",
                "Improve error handling and add connection pooling to database module",
                "in_progress",
                2,
                None
            )
            
            task3_id = db.create_task(
                "Learn about Docker best practices",
                "Research Docker container best practices for microservices architecture",
                "pending",
                1,
                None
            )
            
            logger.info(f"Added sample tasks with IDs: {task1_id}, {task2_id}, {task3_id}")
        
        logger.info("Database setup complete")
    
    except Exception as e:
        logger.error(f"Error setting up database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()