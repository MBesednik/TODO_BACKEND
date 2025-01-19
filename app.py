# main.py
from broker import app, socketio, message_broker
from agents.notification_agent import NotificationAgent
from agents.task_management_agent import TaskManagementAgent
from agents.validation_agent import ValidationAgent
from agents.general_managing_agent import GeneralManagingAgent

from flask import request, jsonify

@app.route('/add_task', methods=['POST'])
def add_task_route():
    task_data = request.get_json()
    print(f"[System] Received request to add task: {task_data}")
    message_broker.emit("generalManager", {
        "type": "add_task",
        "task_data": task_data
    })
    return jsonify({"status": "processing"}), 202

@app.route('/get_tasks', methods=['GET'])
def get_tasks_route():
    print("[System] Received request to fetch all tasks.")
    # Za demonstraciju direktno zovemo TaskManagementAgent get_all_tasks
    tasks = task_agent.get_all_tasks()
    return jsonify({"success": True, "tasks": tasks}), 200

@app.route('/update_task_status', methods=['POST'])
def update_task_status_route():
    data = request.get_json()
    print(f"[System] Received request to update task status: {data}")
    message_broker.emit("generalManager", {
        "type": "update_task_status",
        "task_data": data
    })
    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    # 1) Kreiranje instance agenata
    task_agent = TaskManagementAgent()
    validation_agent = ValidationAgent()
    general_manager = GeneralManagingAgent()
    notification_agent = NotificationAgent()

    # 2) Pokretanje aplikacije
    socketio.run(app, host='127.0.0.1', port=5000, debug=False)
