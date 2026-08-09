from pydantic import BaseModel, Field

from enums import TaskPriority

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=500)
    priority: TaskPriority 