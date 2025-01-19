from broker import message_broker

class ValidationAgent:
    def __init__(self):
        message_broker.register_handler("validate_task", self.handle_message)

    def validate_task(self, task_data):
        errors = []
        if not task_data.get("title"):
            errors.append("Title is required")
        if not task_data.get("description"):
            errors.append("Description is required")
        return len(errors) == 0, errors

    def handle_message(self, data):
        print(f"[ValidationAgent] Received message: {data}")
        if data["type"] == "validate_task":
            is_valid, errors = self.validate_task(data["task_data"])
            if is_valid:
                print("[ValidationAgent] Task validated successfully.")
                # Emisija TaskManagementAgent-u
                message_broker.emit("taskManagementAgent", {
                    "type": "add_task",
                    "task_data": data["task_data"]
                })
            else:
                print(f"[ValidationAgent] Validation failed with errors: {errors}")
                error_message = ", ".join(errors)
                # Emisija NotificationAgent-u
                message_broker.emit("notificationAgent", {
                    "type": "alert",
                    "message": f"Validation failed because: {error_message}"
                })
