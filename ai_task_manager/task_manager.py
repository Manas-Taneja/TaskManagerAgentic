import logging
from typing import List, Dict, Any, Optional
from ai_task_manager.database import TaskDatabase
from ai_task_manager.llm_service import LLMService
from ai_task_manager.search_service import SearchService

logger = logging.getLogger(__name__)

class TaskManager:
    def __init__(self, db=None, search_service=None, llm_service=None):
        self.db = db or TaskDatabase()
        self.search_service = search_service or SearchService()
        self.llm_service = llm_service or LLMService()

    # Task CRUD operations
    def add_task(self, title: str, description: str = "", 
                status: str = "pending", priority: int = 1, 
                due_date: str = None) -> Dict[str, Any]:
        task_id = self.db.create_task(title, description, status, priority, due_date)
        return self.db.get_task(task_id)

    def get_task(self, task_id: int) -> Optional[Dict[str, Any]]:
        return self.db.get_task(task_id)

    def update_task(self, task_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        if self.db.update_task(task_id, **kwargs):
            return self.db.get_task(task_id)
        return None

    def delete_task(self, task_id: int) -> bool:
        return self.db.delete_task(task_id)

    def list_tasks(self, status: str = None, priority: int = None, 
                  limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        return self.db.list_tasks(status, priority, limit, offset)

    # Resource operations
    def search_and_add_resources(self, task_id: int) -> List[Dict[str, Any]]:
        task = self.db.get_task(task_id)
        if not task:
            logger.error(f"Task {task_id} not found")
            return []

        resources = self.search_service.search_for_task(
            task['title'], 
            task.get('description', ''),
            resource_types=['article', 'video', 'tool'],
            num_results=5
        )

        for resource in resources:
            self.db.add_resource(
                task_id,
                resource['title'],
                resource['url'],
                resource.get('type', 'article'),
                resource.get('description', '')
            )

        return self.db.get_resources(task_id)

    # Insight operations
    def generate_and_add_insight(self, task_id: int) -> Optional[Dict[str, Any]]:
        task = self.db.get_task(task_id)
        if not task:
            logger.error(f"Task {task_id} not found")
            return None

        resources = task.get('resources', [])
        if not resources:
            resources = self.search_and_add_resources(task_id)

        insight_content = self.llm_service.generate_task_insights(task, resources)
        insight_id = self.db.add_insight(task_id, insight_content)
        self.db.update_task(task_id)

        task = self.db.get_task(task_id)
        for insight in task.get('insights', []):
            if insight['id'] == insight_id:
                return insight

        return None

    def update_all_tasks(self) -> List[Dict[str, Any]]:
        tasks_to_update = self.db.get_tasks_needing_updates(days_since_update=1)
        updated_tasks = []

        for task in tasks_to_update:
            self.search_and_add_resources(task['id'])
            self.generate_and_add_insight(task['id'])
            updated_tasks.append(self.db.get_task(task['id']))

        return updated_tasks

    def generate_daily_digest(self) -> str:
        tasks = self.db.list_tasks(status='pending') + self.db.list_tasks(status='in_progress')
        return self.llm_service.generate_daily_digest(tasks)
