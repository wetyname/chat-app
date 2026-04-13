from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import json
import os
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key_123'
socketio = SocketIO(app, cors_allowed_origins="*")

USER_DB = "users_data.json"
chat_history = []

# Загрузка базы пользователей
if os.path.exists(USER_DB):
    with open(USER_DB, "r", encoding="utf-8") as f:
        registered_users = json.load(f)
else:
    registered_users = {"adminkgv2015": {"pass": "gkv777555111a?", "email": "admin@chat.com"}}

def save_users():
    with open(USER_DB, "w", encoding="utf-8") as f:
        json.dump(registered_users, f, ensure_ascii=False)

users = {}

@app.route("/")
def index():
    return render_template("index.html")

@socketio.on("authenticate")
def authenticate(data):
    name = data.get("name")
    password = data.get("pass")
    email = data.get("email", "")

    if name in registered_users:
        if registered_users[name]["pass"] == password:
            users[request.sid] = "Костя Г." if name == "adminkgv2015" else name
            emit("auth_success")
            for msg in chat_history:
                emit("message", msg)
        else:
            emit("error_msg", "Невірний пароль!")
    else:
        # Регистрация нового аккаунта с почтой
        registered_users[name] = {"pass": password, "email": email}
        save_users()
        users[request.sid] = name
        emit("auth_success")

@socketio.on("message")
def handle_message(data):
    name = users.get(request.sid, "Гість")
    msg_data = {
        "name": name,
        "msg": data["msg"],
        "is_img": data.get("is_img", False),
        "time": datetime.now().strftime("%H:%M")
    }
    chat_history.append(msg_data)
    if len(chat_history) > 50: chat_history.pop(0)
    emit("message", msg_data, broadcast=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port, allow_unsafe_werkzeug=True)