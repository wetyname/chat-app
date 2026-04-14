from flask import Flask, render_template, request, session, redirect
from flask_socketio import SocketIO, send
import json
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
socketio = SocketIO(app)

DB_FILE = "users.json"

# 📥 загрузка пользователей
def load_users():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except:
            return {}

# 💾 сохранение пользователей
def save_users(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# 🔐 Главная (вход / регистрация)
@app.route("/", methods=["GET", "POST"])
def index():
    users = load_users()

    if request.method == "POST":
        name = request.form.get("name")
        password = request.form.get("password")

        if not name or not password:
            return "❌ Заповни всі поля"

        if name in users:
            # вход
            if users[name]["password"] != password:
                return "❌ Неправильний пароль"
        else:
            # регистрация
            users[name] = {"password": password}
            save_users(users)

        session["name"] = name
        return redirect("/chat")

    return render_template("login.html")

# 💬 Страница чата
@app.route("/chat")
def chat():
    if "name" not in session:
        return redirect("/")
    return render_template("index.html", name=session["name"])

# 👥 Онлайн пользователи
users_online = {}

# 🔌 Подключение
@socketio.on("connect")
def connect():
    name = session.get("name")
    if not name:
        return False

    users_online[request.sid] = name
    send({"type": "system", "msg": f"🟢 {name} приєднався"}, broadcast=True)

# 💬 Сообщения
@socketio.on("message")
def handle_message(data):
    name = users_online.get(request.sid)
    if not name:
        return

    msg = data.get("msg", "")
    if msg == "":
        return

    send({
        "type": "msg",
        "name": name,
        "msg": msg
    }, broadcast=True)

# 🔌 Отключение
@socketio.on("disconnect")
def disconnect():
    if request.sid in users_online:
        name = users_online.pop(request.sid)
        send({"type": "system", "msg": f"🔴 {name} вийшов"}, broadcast=True)

# 🚀 запуск
if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)