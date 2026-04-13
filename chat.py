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
users = {}  # sid: ім'я
banned_users = []

# Завантаження бази користувачів
if os.path.exists(USER_DB):
    with open(USER_DB, "r", encoding="utf-8") as f:
        registered_users = json.load(f)
else:
    # Початковий адмін
    registered_users = {"adminkgv2015": {"pass": "gkv777555111a?", "email": "admin@chat.com"}}

# Завантаження бан-листа
if os.path.exists(BAN_FILE):
    with open(BAN_FILE, "r", encoding="utf-8") as f:
        banned_users = json.load(f)

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

    if not login or not password:
        emit("error_msg", "Введіть нік та пароль!")
        return

    if login in banned_users:
        emit("error_msg", "Ви забанені!")
        return

    if login in registered_users:
        # Перевірка пароля для існуючого користувача
        if registered_users[login]["pass"] == password:
            display_name = "Костя Гончаров" if login == "adminkgv2015" else login
            users[request.sid] = display_name
            emit("auth_success")
            for msg in chat_history:
                emit("message", msg)
        else:
            emit("error_msg", "Невірний пароль!")
    else:
        # Реєстрація нового користувача: зберігаємо нік, пароль та пошту
        registered_users[login] = {"pass": password, "email": email}
        save_data(USER_DB, registered_users)

        users[request.sid] = login
        emit("auth_success")

        reg_msg = {
            "name": "Система",
            "msg": f"{login} зареєструвався!",
            "is_sys": True,
            "time": datetime.now().strftime("%H:%M")
        }
        emit("message", reg_msg, broadcast=True)

@socketio.on("message")
def handle_message(data):
    name = users.get(request.sid)
    if not name or name in banned_users: return

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