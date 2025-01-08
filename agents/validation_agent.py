class ValidationAgent:
    def validate_task(self, task_data):
        errors = []
        if not task_data.get("title"):
            errors.append("Title is required.")
        if not task_data.get("description"):
            errors.append("Description is required.")
        return len(errors) == 0, errors
