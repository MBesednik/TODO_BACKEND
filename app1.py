from flask import Flask
from flask_socketio import SocketIO, emit
from threading import Thread
import time

# Inicijalizacija Flask aplikacije
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
# Inicijalizacija SocketIO s dozvoljenim CORS originima
socketio = SocketIO(app, cors_allowed_origins="*")


# Inicijalizacija agenata
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
        print(f"[TaskManagementAgent] Task added: {task}")
        return task

    def handle_message(self, data):
        print(f"[TaskManagementAgent] Received message: {data}")
        if data["type"] == "add_task":
            task = self.add_task(data["task_data"])
            emit('TaskManagementAgent_response', {"status": "success", "task": task}, broadcast=True)


class ValidationAgent:
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
                print(f"[ValidationAgent] Task validated successfully.")
                # Emit a message to TaskManagementAgent to add the task
                socketio.emit('TaskManagementAgent_message', {
                    "type": "add_task",
                    "task_data": data["task_data"]
                }, broadcast=True)
            else:
                print(f"[ValidationAgent] Validation failed with errors: {errors}")
                emit('ValidationAgent_response', {"is_valid": is_valid, "errors": errors}, broadcast=True)


# Inicijalizacija agenata
task_agent = TaskManagementAgent()
validation_agent = ValidationAgent()


# WebSocket događaji za svakog agenta
@socketio.on('TaskManagementAgent_message')
def handle_task_management_message(data):
    task_agent.handle_message(data)


@socketio.on('ValidationAgent_message')
def handle_validation_message(data):
    validation_agent.handle_message(data)


# Testiranje unutar BE (simulacija komunikacije)
def simulate_internal_communication():
    """
    Simulira BE-to-BE komunikaciju između ValidationAgent-a i TaskManagementAgent-a.
    """
    time.sleep(2)  # Pauza kako bi server mogao pokrenuti sve procese
    print("[System] Sending message to ValidationAgent...")
    # Emitiraj poruku ValidationAgent-u
    socketio.emit('ValidationAgent_message', {
        "type": "validate_task",
        "task_data": {
            "title": "Internal Task",
            "description": "This is a task sent internally for validation."
        }
    }, to=None)  # Emitiraj svima


if __name__ == '__main__':
    # Pokreni simulaciju komunikacije u pozadinskoj niti
    Thread(target=simulate_internal_communication).start()
    # Pokreni SocketIO server
    socketio.run(app, host='127.0.0.1', port=5000, debug=True)
