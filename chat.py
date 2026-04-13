from flask import Flask, render_template, request, session, redirect
from flask_socketio import SocketIO, send, emit
import re

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
socketio = SocketIO(app)

# 👑 админ
ADMIN_NAME = "admin"
ADMIN_PASSWORD = "1234"

# 🚫 мат
bad_words = ["блять", "сука", "хуй", "пизда"]

def clean_text(text):
    return re.sub(r'[^а-яА-Яa-zA-Z]', '', text.lower())

# 📊 данные
users = {}
banned = set()
messages = []

# 🌐 страницы

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        name = request.form.get("name")
        password = request.form.get("password")

        if name in banned:
            return "Ти забанений 🚫"

        session["name"] = name
        session["password"] = password
        return redirect("/chat")

    return """
    <h2>Вхід</h2>
    <form method="POST">
        <input name="name" placeholder="Нік"><br><br>
        <input name="password" type="password" placeholder="Пароль"><br><br>
        <button type="submit">Увійти</button>
    </form>
    """

@app.route("/chat")
def chat():
    if "name" not in session:
        return redirect("/")

    return render_template("index.html", name=session["name"])

# 🔌 сокеты

@socketio.on("connect")
def connect():
    name = session.get("name")
    password = session.get("password")

    if not name:
        return False

    is_admin = (name == ADMIN_NAME and password == ADMIN_PASSWORD)
    users[request.sid] = {"name": name, "admin": is_admin}

    msg = "👑 Адмін зайшов" if is_admin else f"🟢 {name} приєднався"
    messages.append({"type":"system","msg":msg})
    send({"type":"system","msg":msg}, broadcast=True)

    # отправка истории
    for m in messages:
        send(m)

@socketio.on("message")
def handle_message(data):
    user = users.get(request.sid)
    if not user:
        return

    name = user["name"]
    msg = data["msg"]
    is_img = data.get("is_img", False)

    # 🔨 бан
    if msg.startswith("/ban ") and user["admin"]:
        target = msg.split(" ", 1)[1]
        banned.add(target)
        send({"type":"system","msg":f"🔨 {target} забанений"}, broadcast=True)
        return

    # 🚫 мат
    if not is_img:
        clean = clean_text(msg)
        for word in bad_words:
            if word in clean:
                send({"type":"system","msg":f"🚫 {name}, не можна писати так 😡"})
                return

    msg_data = {"type":"msg","name":name,"msg":msg,"is_img":is_img}
    messages.append(msg_data)
    send(msg_data, broadcast=True)

@socketio.on("disconnect")
def disconnect():
    if request.sid in users:
        name = users[request.sid]["name"]
        users.pop(request.sid)

        msg = {"type":"system","msg":f"🔴 {name} вийшов"}
        messages.append(msg)
        emit("message", msg, broadcast=True)

# 🚀 запуск
if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)
