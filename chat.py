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
users = {}  # Храним sid: имя
banned_users = []

# Список плохих слов (добавь свои через запятую)
BAD_WORDS = ["плохоеслово1", "плохоеслово2"]

# Загрузка базы пользователей
if os.path.exists(USER_DB):
    with open(USER_DB, "r", encoding="utf-8") as f:
        registered_users = json.load(f)
else:
    registered_users = {"adminkgv2015": {"pass": "gkv777555111a?", "email": "admin@chat.com"}}

# Загрузка бан-листа
if os.path.exists(BAN_FILE):
    with open(BAN_FILE, "r", encoding="utf-8") as f:
        banned_users = json.load(f)


def save_data(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)


def filter_text(text):
    for word in BAD_WORDS:
        if word.lower() in text.lower():
            text = text.replace(word, "***")
    return text


@app.route("/")
def index():
    return render_template("index.html")


@socketio.on("authenticate")
def authenticate(data):
    login = data.get("name")
    password = data.get("pass")
    email = data.get("email", "")

    if login in banned_users:
        emit("error_msg", "Ви забанені!")
        return

    # Поиск по имени или почте
    user_key = None
    for name, info in registered_users.items():
        if name == login or info.get("email") == login:
            user_key = name
            break

    if user_key:
        if registered_users[user_key]["pass"] == password:
            display_name = "Костя Г." if user_key == "adminkgv2015" else user_key
            users[request.sid] = display_name
            emit("auth_success")
            for msg in chat_history: emit("message", msg)

            # Системное сообщение о входе
            join_msg = {"name": "Система", "msg": f"{display_name} зайшов у чат", "is_sys": True,
                        "time": datetime.now().strftime("%H:%M")}
            emit("message", join_msg, broadcast=True)
        else:
            emit("error_msg", "Невірний пароль!")
    else:
        # Регистрация
        registered_users[login] = {"pass": password, "email": email}
        save_data(USER_DB, registered_users)
        users[request.sid] = login
        emit("auth_success")


@socketio.on("message")
def handle_message(data):
    name = users.get(request.sid)
    if not name or name in banned_users: return

    text = data["msg"]

    # Команда бана (только для админа)
    if text.startswith("/ban ") and name == "Костя Г.":
        victim = text.replace("/ban ", "").strip()
        if victim not in banned_users:
            banned_users.append(victim)
            save_data(BAN_FILE, banned_users)
            emit("message", {"name": "Система", "msg": f"{victim} забанений!", "is_sys": True}, broadcast=True)
        return

    # Фильтр мата и отправка
    clean_text = filter_text(text)
    msg_data = {
        "name": name,
        "msg": clean_text,
        "is_img": data.get("is_img", False),
        "time": datetime.now().strftime("%H:%M")
    }
    chat_history.append(msg_data)
    if len(chat_history) > 50: chat_history.pop(0)
    emit("message", msg_data, broadcast=True)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port, allow_unsafe_werkzeug=True)