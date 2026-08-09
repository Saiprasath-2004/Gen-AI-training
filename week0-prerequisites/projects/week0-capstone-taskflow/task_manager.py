from datetime import datetime

from enums import TaskStatus
from models import Task
from validators import TaskCreate
from storage import save_tasks, load_tasks
from logger import logger

class TaskManager:
    def __init__(self):
        self.tasks = load_tasks()
        if self.tasks:
            self.next_id = max(
                task.id for task in self.tasks
            ) + 1

        else: 
            self.next_id = 1

    def create_task(self, task_create: TaskCreate) -> Task:

        task = Task(
            id = self.next_id,
            title = task_create.title,
            description = task_create.description,
            priority = task_create.priority,
            status = TaskStatus.PENDING,
            created_at = datetime.now(),
        )

        
        logger.info(
            f"Creating task: {task.title}"
        )
        self.tasks.append(task)
        save_tasks(self.tasks)

        logger.info(
            f"Task created successfully: {task.id}"
        )
        self.next_id += 1
        return task 

    def list_tasks(self):
        return self.tasks