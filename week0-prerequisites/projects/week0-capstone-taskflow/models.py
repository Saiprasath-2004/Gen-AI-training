from dataclasses import dataclass
from datetime import datetime

from enums import TaskStatus , TaskPriority

@dataclass
class Task:
    id: int
    title: str
    description: str
    status: TaskStatus
    priority: TaskPriority
    created_at: datetime

    