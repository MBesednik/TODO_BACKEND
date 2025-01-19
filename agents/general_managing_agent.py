from broker import message_broker

class GeneralManagingAgent:
    def __init__(self):
        message_broker.register_handler("generalManager", self.handle_message)

    def handle_message(self, data):
        print(f"[GeneralManagingAgent] Received message: {data}")
        request_type = data.get("type")

        if request_type == "add_task":
            # Prvo ValidationAgent
            message_broker.emit("validate_task", {
                "type": "validate_task",
                "task_data": data["task_data"]
            })
        elif request_type == "get_all_tasks":
            message_broker.emit("taskManagementAgent", {
                "type": "get_all_tasks"
            })
        elif request_type == "update_task_status":
            message_broker.emit("taskManagementAgent", {
                "type": "update_task_status",
                "task_data": data["task_data"]
            })
        else:
            print(f"[GeneralManagingAgent] Unknown request type: {request_type}")
