from flask import Flask, render_template, request
from flask_socketio import SocketIO, send, emit
import re

# 🔐 Админ
ADMIN_NAME = "admin"
ADMIN_PASSWORD = "gkv777555111a?"

# 🚫 Мат-фильтр
bad_words = ["блять", "сука", "хуй", "пизда"]

def clean_text(text):
    return re.sub(r'[^а-яА-Яa-zA-Z]', '', text.lower())

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# 📊 Данные
users = {}
banned = set()
messages = []

@app.route("/")
def index():
    return render_template("index.html")

# 👤 Вход
@socketio.on("join")
def on_join(data):
    name = data["name"]
    password = data.get("password", "")

    if name in banned:
        emit("message", {"type":"system","msg":"🚫 Ти забанений"})
        return

    is_admin = (name == ADMIN_NAME and password == ADMIN_PASSWORD)

    users[request.sid] = {"name": name, "admin": is_admin}

    msg = "👑 Адмін зайшов" if is_admin else f"🟢 {name} приєднався"
    messages.append({"type":"system","msg":msg})
    send({"type":"system","msg":msg}, broadcast=True)

# 💬 Сообщения
@socketio.on("message")
def handle_message(data):
    user = users.get(request.sid)
    if not user:
        return

    name = user["name"]
    msg = data["msg"]
    is_img = data.get("is_img", False)

    # 🔨 Бан
    if msg.startswith("/ban ") and user["admin"]:
        target = msg.split(" ", 1)[1]
        banned.add(target)
        send({"type":"system","msg":f"🔨 {target} забанений"}, broadcast=True)
        return

    # 🚫 Мат
    if not is_img:
        clean = clean_text(msg)
        for word in bad_words:
            if word in clean:
                send({"type":"system","msg":f"🚫 {name}, не можна писати так 😡"})
                return

    msg_data = {"type":"msg","name":name,"msg":msg,"is_img":is_img}
    messages.append(msg_data)
    send(msg_data, broadcast=True)

# 🔌 Выход
@socketio.on("disconnect")
def on_disconnect():
    if request.sid in users:
        name = users[request.sid]["name"]
        users.pop(request.sid)

        msg = {"type":"system","msg":f"🔴 {name} покинув чат"}
        messages.append(msg)
        emit("message", msg, broadcast=True)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)