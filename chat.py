from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import json
import os
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key_123'
socketio = SocketIO(app, cors_allowed_origins="*")

USER_DB = "users_data.json"
BAN_FILE = "banned.json"
chat_history = []
users = {}

# Загрузка данных
if os.path.exists(USER_DB):
    with open(USER_DB, "r", encoding="utf-8") as f:
        registered_users = json.load(f)
else:
    registered_users = {"adminkgv2015": {"pass": "gkv777555111a?", "email": "admin@chat.com"}}

if os.path.exists(BAN_FILE):
    with open(BAN_FILE, "r", encoding="utf-8") as f:
        banned_users = json.load(f)
else:
    banned_users = []

def save_data(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

@app.route("/")
def index():
    return render_template("index.html")

@socketio.on("authenticate")
def authenticate(data):
    login = data.get("name", "").strip()
    password = data.get("pass", "").strip()
    email = data.get("email", "").strip()

    if login in banned_users or email in banned_users:
        emit("error_msg", "Ви забанені!")
        return

    # Вход по почте или логину
    user_found = None
    if login in registered_users:
        user_found = login
    else:
        # Ищем, есть ли такая почта у кого-то из зарегистрированных
        for u_name, u_data in registered_users.items():
            if u_data.get("email") == email:
                user_found = u_name
                break

    if user_found:
        if registered_users[user_found]["pass"] == password:
            display_name = "Костя Гончаров" if user_found == "adminkgv2015" else user_found
            users[request.sid] = display_name
            emit("auth_success")
            for msg in chat_history:
                emit("message", msg)
        else:
            emit("error_msg", "Невірний пароль!")
    else:
        # Регистрация нового пользователя
        registered_users[login] = {"pass": password, "email": email}
        save_data(USER_DB, registered_users)
        users[request.sid] = login
        emit("auth_success")

@socketio.on("message")
def handle_message(data):
    name = users.get(request.sid)
    if not name or name in banned_users:
        return

    text = data.get("msg", "").strip()

    # Команда бана (только для админа)
    if text.startswith("/ban ") and name == "Костя Гончаров":
        victim = text.replace("/ban ", "").strip()
        if victim not in banned_users:
            banned_users.append(victim)
            save_data(BAN_FILE, banned_users)
            emit("message", {"name": "Система", "msg": f"{victim} забанений!", "is_sys": True, "time": datetime.now().strftime("%H:%M")}, broadcast=True)
        return

    msg_data = {
        "name": name,
        "msg": text,
        "is_img": data.get("is_img", False),
        "time": datetime.now().strftime("%H:%M")
    }
    chat_history.append(msg_data)
    if len(chat_history) > 50: chat_history.pop(0)
    emit("message", msg_data, broadcast=True)