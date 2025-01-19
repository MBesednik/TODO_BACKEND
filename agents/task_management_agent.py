# agents/task_management_agent.py

import os
import json
import time
from threading import Thread
from broker import message_broker  # tu je i app, socketio, ali izravni socketio.emit više ne koristimo
# izbjegavamo "from broker import socketio" jer emitamo NotificationAgentom

class TaskManagementAgent:
    def __init__(self):
        self.tasks = []
        self.task_id_counter = 1
        self.storage_file = "tasks_data.json"

        message_broker.register_handler("taskManagementAgent", self.handle_message)

        # Učitaj zadatke iz datoteke
        self.load_tasks_from_file()

        # Periodički behavior
        self._start_periodic_behavior()

    def load_tasks_from_file(self):
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.tasks = data.get("tasks", [])
                    self.task_id_counter = data.get("task_id_counter", 1)
                print(f"[TaskManagementAgent] Loaded {len(self.tasks)} tasks from {self.storage_file}")
            except Exception as e:
                print(f"[TaskManagementAgent] Error loading tasks from file: {e}")
        else:
            print("[TaskManagementAgent] No JSON file found. Starting empty.")

    def save_tasks_to_file(self):
        data = {
            "tasks": self.tasks,
            "task_id_counter": self.task_id_counter
        }
        try:
            with open(self.storage_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            print(f"[TaskManagementAgent] Tasks saved to {self.storage_file}")
        except Exception as e:
            print(f"[TaskManagementAgent] Error saving tasks: {e}")

    def _start_periodic_behavior(self):
        t = Thread(target=self._periodic_task, daemon=True)
        t.start()

    def _periodic_task(self):
        while True:
            time.sleep(15)
            print("[TaskManagementAgent] 15s passed -> Reloading and sending new data out.")
            # Ponovno učitaj (ako je netko ručno mijenjao JSON)
            self.load_tasks_from_file()

            # Emitiraj "tasks_updated" poruku NotificationAgentu
            tasks = self.get_all_tasks()
            message_broker.emit("notificationAgent", {
                "type": "tasks_updated",
                "tasks": tasks
            })
            print(f"[TaskManagementAgent] Emitted all tasks to NotificationAgent: {tasks}")

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

        # Snimimo u JSON
        self.save_tasks_to_file()

        print(f"[TaskManagementAgent] Task added: {task}")

        # 1) Obavijest da je task kreiran
        message_broker.emit("notificationAgent", {
            "type": "task_added",
            "message": f"Task with ID {task['id']} has been created"
        })
        # 2) Ažurirani popis
        message_broker.emit("notificationAgent", {
            "type": "tasks_updated",
            "tasks": self.get_all_tasks()
        })

    def update_task_status(self, task_data):
        task_id = task_data.get("task_id")
        new_status = task_data.get("new_status")

        for task in self.tasks:
            if task["id"] == task_id:
                for status_obj in task["status"]:
                    status_obj["selected"] = (status_obj["name"] == new_status)
                print(f"[TaskManagementAgent] Task ID {task_id} status updated to '{new_status}'")
                break

        self.save_tasks_to_file()

        # Obavijest o tasks_updated
        message_broker.emit("notificationAgent", {
            "type": "tasks_updated",
            "tasks": self.get_all_tasks()
        })

        if new_status == "Done":
            message_broker.emit("notificationAgent", {
                "type": "alert",
                "message": f"Task {task_id} update its status to {new_status}"
            })

    def get_all_tasks(self):
        grouped_tasks = {"To Do": [], "In Progress": [], "Done": []}
        for t in self.tasks:
            for st in t["status"]:
                if st["selected"]:
                    grouped_tasks[st["name"]].append(t)
                    break
        return grouped_tasks

    def handle_message(self, data):
        print(f"[TaskManagementAgent] Received message: {data}")
        msg_type = data["type"]
        if msg_type == "add_task":
            self.add_task(data["task_data"])
        elif msg_type == "get_all_tasks":
            tasks = self.get_all_tasks()
            message_broker.emit("notificationAgent", {
                "type": "tasks_updated",
                "tasks": tasks
            })
        elif msg_type == "update_task_status":
            self.update_task_status(data["task_data"])
