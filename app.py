from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from agents.task_management_agent import TaskManagementAgent
from agents.validation_agent import ValidationAgent
from flask_cors import CORS

# Inicijalizacija Flask aplikacije
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")  # Enable CORS for SocketIO
CORS(app)  # Enable CORS for all routes


# Inicijalizacija agenata
task_agent = TaskManagementAgent()
validation_agent = ValidationAgent()

@app.route('/')
def index():
    return "Task Management System is running."

@app.route('/add_task', methods=['POST'])
def add_task():
    data = request.json
    # Validate and add the task
    is_valid, errors = validation_agent.validate_task(data)
    if not is_valid:
        return jsonify({"success": False, "errors": errors}), 400

    task_agent.add_task(data)
    # Fetch all tasks after adding the new task
    all_tasks = task_agent.get_all_tasks()

    # Notify all clients with the updated list of tasks
    socketio.emit('tasks_updated', all_tasks)

    return jsonify({"success": True}), 201

@app.route('/get_tasks', methods=['GET'])
def get_tasks():
    tasks = task_agent.get_all_tasks()
    
    return jsonify({"success": True, "tasks": tasks}), 200

@app.route('/update_task_status/<int:task_id>', methods=['PUT'])
def update_task_status(task_id):
    data = request.json
    new_status = data.get("status")

    # Provjera valjanosti statusa
    if new_status not in ["To Do", "In Progress", "Done"]:
        return jsonify({"success": False, "error": "Invalid status"}), 400

    # Ažuriranje statusa
    updated_task = task_agent.update_task_status(task_id, new_status)
    if updated_task:
        all_tasks = task_agent.get_all_tasks()
        # Notify all clients with the updated list of tasks
        socketio.emit('tasks_updated', all_tasks)
        return jsonify({"success": True, "task": updated_task}), 200

    return jsonify({"success": False, "error": "Task not found"}), 404



# WebSocket događaj za testiranje
@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    socketio.run(app, host='127.0.0.1', port=5000, debug=True)
