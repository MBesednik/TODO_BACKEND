from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS

class MessageBroker:
    def __init__(self):
        self.handlers = {}

    def register_handler(self, event_type, handler):
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)

    def emit(self, event_type, data):
        if event_type in self.handlers:
            for handler in self.handlers[event_type]:
                handler(data)
        else:
            print(f"[MessageBroker] No handlers for event: {event_type}")

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"
socketio = SocketIO(app, cors_allowed_origins="*")

CORS(app)
message_broker = MessageBroker()
