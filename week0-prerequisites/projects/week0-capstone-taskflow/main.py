from validators import TaskCreate
from task_manager import TaskManager

manager = TaskManager()

task = TaskCreate(
    title = "Learn Pydantic",
    description="Understand validation",
    priority="HIGH"
)

task_input = TaskCreate(
    title="Learn Async",
    description="Understand concurrency",
    priority="MEDIUM"
)

task = manager.create_task(task)
task_input = manager.create_task(task_input)

print(task) 

print()

print("All Tasks:")
for task in manager.list_tasks():
    print(task)