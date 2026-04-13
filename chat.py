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
banned_users = []

# Загрузка базы пользователей
if os.path.exists(USER_DB):
    with open(USER_DB, "r", encoding="utf-8") as f:
        registered_users = json.load(f)
else:
    registered_users = {"adminkgv2015": {"pass": "gkv777555111a?", "email": "admin@chat.com"}}

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

    if login in banned_users:
        emit("error_msg", "Ви забанені!")
        return

    if login in registered_users:
        if registered_users[login]["pass"] == password:
            display_name = "Костя Гончаров" if login == "adminkgv2015" else login
            users[request.sid] = display_name
            emit("auth_success")
            for msg in chat_history:
                emit("message", msg)
        else:
            emit("error_msg", "Невірний пароль!")
    else:
        # Регистрация: сохраняем НИК, ПАРОЛЬ и ПОЧТУ
        registered_users[login] = {"pass": password, "email": email}
        save_data(USER_DB, registered_users)
        users[request.sid] = login
        emit("auth_success")

        reg_msg = {"name": "Система", "msg": f"{login} приєднався!", "is_sys": True,
                   "time": datetime.now().strftime("%H:%M")}
        emit("message", reg_msg, broadcast=True)


@socketio.on("message")
def handle_message(data):
    # 1. Отримуємо ім'я користувача за його ID (sid)
    name = users.get(request.sid)

    # 2. Якщо користувача немає в списку або він забанений — ігноруємо
    if not name or name in banned_users:
        return

    # 3. Отримуємо текст повідомлення
    text = data.get("msg", "").strip()

    # --- БЛОК МОДЕРАЦІЇ (Команда /ban) ---
    # Перевіряємо, чи текст починається з /ban і чи відправник — адмін
    # ВАЖЛИВО: Ім'я має точно збігатися з тим, що вказано в authenticate
    if text.startswith("/ban ") and name == "Костя Гончаров":
        # Вирізаємо нік жертви (все, що після "/ban ")
        victim = text.replace("/ban ", "").strip()

        if victim not in banned_users:
            banned_users.append(victim)
            save_data(BAN_FILE, banned_users)

            # Повідомляємо всіх про бан
            emit("message", {
                "name": "Система",
                "msg": f"Користувач {victim} був забанений!",
                "is_sys": True,
                "time": datetime.now().strftime("%H:%M")
            }, broadcast=True)
        return  # Виходимо, щоб сама команда не з'явилася в чаті як повідомлення
    # -------------------------------------

    # 4. Формуємо звичайне повідомлення для чату
    msg_data = {
        "name": name,
        "msg": text,
        "is_img": data.get("is_img", False),  # Перевірка, чи це картинка
        "time": datetime.now().strftime("%H:%M")
    }

    # 5. Зберігаємо в історію (максимум 50 повідомлень)
    chat_history.append(msg_data)
    if len(chat_history) > 50:
        chat_history.pop(0)

    # 6. Надсилаємо повідомлення всім учасникам
    emit("message", msg_data, broadcast=True)
    if __name__ == '__main__':
        socketio.run(app, debug=True)