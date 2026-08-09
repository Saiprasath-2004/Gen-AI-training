import json

from dataclasses import asdict
from datetime import datetime

from enums import TaskPriority,TaskStatus
from models import Task

def save_tasks(tasks, filename="tasks.json"):

    task_data = []

    for task in tasks:
        task_data.append(asdict(task)) 

    with open(filename, "w") as file:
        json.dump(task_data, file, indent = 4, default = str)

def load_tasks(filename="tasks.json"):

    try:
        with open(filename, "r") as file:
            task_data = json.load(file)
            tasks = []

            for item in task_data:
                task = Task(
                    id = item["id"],
                    title = item["title"],
                    description = item["description"],
                    priority = TaskPriority(item["priority"]),
                    status = TaskStatus(item["status"]),
                    created_at = datetime.fromisoformat(
                        item["created_at"]
                    ),
                )

                tasks.append(task)

            return tasks

    except FileNotFoundError:
        return []

    except json.JSONDecodeError:
        return  []