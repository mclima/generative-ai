import uuid
from typing import Dict, Optional, List
from datetime import datetime
import asyncio
from enum import Enum

class TaskStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class TaskManager:
    """Manages async tasks for resume matching"""
    
    def __init__(self):
        self.tasks: Dict[str, Dict] = {}
    
    def create_task(self) -> str:
        """Create a new task and return its ID"""
        task_id = str(uuid.uuid4())
        self.tasks[task_id] = {
            "id": task_id,
            "status": TaskStatus.PENDING,
            "progress": 0,
            "result": None,
            "error": None,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        return task_id
    
    def update_task(self, task_id: str, status: TaskStatus, progress: int = 0, 
                   result: Optional[List] = None, error: Optional[str] = None):
        """Update task status and data"""
        if task_id in self.tasks:
            self.tasks[task_id].update({
                "status": status,
                "progress": progress,
                "result": result,
                "error": error,
                "updated_at": datetime.now().isoformat()
            })
    
    def get_task(self, task_id: str) -> Optional[Dict]:
        """Get task by ID"""
        return self.tasks.get(task_id)
    
    def cleanup_old_tasks(self, max_age_minutes: int = 60):
        """Remove tasks older than max_age_minutes"""
        now = datetime.now()
        to_remove = []
        
        for task_id, task in self.tasks.items():
            created_at = datetime.fromisoformat(task["created_at"])
            age_minutes = (now - created_at).total_seconds() / 60
            
            if age_minutes > max_age_minutes:
                to_remove.append(task_id)
        
        for task_id in to_remove:
            del self.tasks[task_id]

# Global task manager instance
task_manager = TaskManager()
