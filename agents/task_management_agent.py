class TaskManagementAgent:
    def __init__(self):
        self.tasks = []
        self.task_id_counter = 1

    def add_task(self, task_data):
        task = {
            "id": self.task_id_counter,
            "title": task_data.get("title"),
            "status": [
                {"name": "To Do", "selected": True},
                {"name": "In Progress", "selected": False},
                {"name": "Done", "selected": False},
            ],
            "description": task_data.get("description"),
            "completed": False
        }
        self.tasks.append(task)
        self.task_id_counter += 1
        return task
    
    def get_all_tasks(self):
        # Group tasks by status
        grouped_tasks = {"To Do": [], "In Progress": [], "Done": []}
        for task in self.tasks:
            for status in task["status"]:
                if status["selected"]:  # Check the selected status
                    grouped_tasks[status["name"]].append(task)
                    break
        return grouped_tasks

    def update_task_status(self, task_id, new_status):
        for task in self.tasks:
            if task["id"] == task_id:
                for status in task["status"]:
                    status["selected"] = (status["name"] == new_status)
                return task
        return None
