from broker import message_broker, socketio

class NotificationAgent:
    def __init__(self):
        # Registriramo se na "notificationAgent"
        message_broker.register_handler("notificationAgent", self.handle_message)

    def handle_message(self, data):
        print(f"[NotificationAgent] Received data: {data}")
        event_type = data.get("type")

        if event_type == "tasks_updated":
            tasks = data.get("tasks", [])
            socketio.emit("tasks_updated", tasks)
        elif event_type == "alert":
            msg = data.get("message", "No message provided")
            socketio.emit("alert", msg)
        elif event_type == "task_added":
            msg = data.get("message", "")
            socketio.emit("task_added", msg)
        else:
            print(f"[NotificationAgent] Unknown event type: {event_type}")
