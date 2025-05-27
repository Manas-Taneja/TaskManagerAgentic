# ai_task_manager/utils.py
import os
import json
import logging
from datetime import datetime, date
from typing import Dict, Any, Union

logger = logging.getLogger(__name__)

def validate_date(date_str: str) -> bool:
    """Validate a date string in YYYY-MM-DD format."""
    if not date_str:
        return False
        
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def format_date(date_obj: Union[str, datetime, date]) -> str:
    """Format a date object or string to YYYY-MM-DD format."""
    if isinstance(date_obj, str):
        if validate_date(date_obj):
            return date_obj
        else:
            try:
                date_obj = datetime.strptime(date_obj, "%Y-%m-%d")
            except ValueError:
                return ""
    
    if isinstance(date_obj, (datetime, date)):
        return date_obj.strftime("%Y-%m-%d")
    
    return ""

def safe_json_serialize(obj: Any) -> Any:
    """Convert objects to JSON serializable format."""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    return str(obj)

def export_tasks_to_json(tasks: list, output_path: str) -> bool:
    """Export tasks to a JSON file."""
    try:
        with open(output_path, "w") as f:
            json.dump(tasks, f, default=safe_json_serialize, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error exporting tasks to JSON: {e}")
        return False

def import_tasks_from_json(input_path: str) -> list:
    """Import tasks from a JSON file."""
    try:
        with open(input_path, "r") as f:
            tasks = json.load(f)
        return tasks
    except Exception as e:
        logger.error(f"Error importing tasks from JSON: {e}")
        return []

def get_priority_label(priority: int) -> str:
    """Convert numeric priority to text label."""
    priority_labels = {
        1: "Low",
        2: "Medium-Low",
        3: "Medium",
        4: "Medium-High",
        5: "High"
    }
    return priority_labels.get(priority, "Unknown")

def get_status_emoji(status: str) -> str:
    """Get emoji for task status."""
    status_emojis = {
        "pending": "⏳",
        "in_progress": "🔄",
        "completed": "✅",
        "blocked": "🚫",
        "canceled": "❌"
    }
    return status_emojis.get(status.lower(), "❓")