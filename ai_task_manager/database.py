# ai_task_manager/database.py
import os
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any, Optional


class TaskDatabase:
    def __init__(self, db_path=None):
        if db_path is None:
            db_path = os.getenv("DB_PATH", "ai_task_manager.db")
        
        self.db_path = db_path
        self._ensure_tables()
    
    def _ensure_tables(self):
        """Create tables if they don't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tasks table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'pending',
            priority INTEGER DEFAULT 1,
            due_date TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Resources table (for links, articles, etc.)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS resources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            url TEXT NOT NULL,
            type TEXT,
            description TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (task_id) REFERENCES tasks (id) ON DELETE CASCADE
        )
        ''')
        
        # Insights table (for LLM-generated insights)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS insights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (task_id) REFERENCES tasks (id) ON DELETE CASCADE
        )
        ''')
        
        conn.commit()
        conn.close()
    
    # Task CRUD operations
    def create_task(self, title: str, description: str = "", status: str = "pending", 
                   priority: int = 1, due_date: str = None) -> int:
        """Create a new task and return its ID."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        cursor.execute(
            "INSERT INTO tasks (title, description, status, priority, due_date, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (title, description, status, priority, due_date, now, now)
        )
        
        task_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return task_id
    
    def get_task(self, task_id: int) -> Optional[Dict[str, Any]]:
        """Get a task by ID with its resources and insights."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get task
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        task_row = cursor.fetchone()
        
        if not task_row:
            conn.close()
            return None
        
        task = dict(task_row)
        
        # Get resources
        cursor.execute("SELECT * FROM resources WHERE task_id = ?", (task_id,))
        resources = [dict(row) for row in cursor.fetchall()]
        task['resources'] = resources
        
        # Get insights
        cursor.execute("SELECT * FROM insights WHERE task_id = ?", (task_id,))
        insights = [dict(row) for row in cursor.fetchall()]
        task['insights'] = insights
        
        conn.close()
        return task
    
    def update_task(self, task_id: int, **kwargs) -> bool:
        """Update a task's fields."""
        if not kwargs:
            return False
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Build update query
        allowed_fields = {'title', 'description', 'status', 'priority', 'due_date'}
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not updates:
            conn.close()
            return False
            
        # Add updated_at timestamp
        updates['updated_at'] = datetime.now().isoformat()
        
        # Construct and execute query
        set_clause = ", ".join(f"{k} = ?" for k in updates.keys())
        values = list(updates.values())
        
        cursor.execute(
            f"UPDATE tasks SET {set_clause} WHERE id = ?",
            values + [task_id]
        )
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    def delete_task(self, task_id: int) -> bool:
        """Delete a task by ID."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    def list_tasks(self, status: str = None, priority: int = None, 
                  limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """List tasks with optional filtering."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT * FROM tasks"
        params = []
        
        # Apply filters
        conditions = []
        if status:
            conditions.append("status = ?")
            params.append(status)
        
        if priority:
            conditions.append("priority = ?")
            params.append(priority)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        # Add pagination
        query += " ORDER BY priority DESC, created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        tasks = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return tasks
    
    # Resource operations
    def add_resource(self, task_id: int, title: str, url: str, 
                    resource_type: str = "article", description: str = "") -> int:
        """Add a resource to a task."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO resources (task_id, title, url, type, description) VALUES (?, ?, ?, ?, ?)",
            (task_id, title, url, resource_type, description)
        )
        
        resource_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return resource_id
    
    def get_resources(self, task_id: int) -> List[Dict[str, Any]]:
        """Get all resources for a task."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM resources WHERE task_id = ?", (task_id,))
        resources = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return resources
    
    # Insight operations
    def add_insight(self, task_id: int, content: str) -> int:
        """Add an LLM-generated insight to a task."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO insights (task_id, content) VALUES (?, ?)",
            (task_id, content)
        )
        
        insight_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return insight_id
    
    def get_insights(self, task_id: int) -> List[Dict[str, Any]]:
        """Get all insights for a task."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM insights WHERE task_id = ?", (task_id,))
        insights = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return insights
    
    def get_tasks_needing_updates(self, days_since_update: int = 1) -> List[Dict[str, Any]]:
        """Get tasks that haven't been updated recently."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(
            """SELECT t.* FROM tasks t
               LEFT JOIN (
                   SELECT task_id, MAX(created_at) as last_insight
                   FROM insights
                   GROUP BY task_id
               ) i ON t.id = i.task_id
               WHERE i.last_insight IS NULL 
               OR datetime(i.last_insight) < datetime('now', ? || ' days')
               ORDER BY t.priority DESC
            """,
            (f"-{days_since_update}",)
        )
        
        tasks = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return tasks