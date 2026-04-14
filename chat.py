from flask import Flask, render_template, request, session, redirect
from flask_socketio import SocketIO, send
import json
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
socketio = SocketIO(app)

DB_FILE = "users.json"

def load_users():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except:
            return {}

def save_users(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

@app.route("/", methods=["GET", "POST"])
def index():
    users = load_users()
    if request.method == "POST":
        name = request.form.get("name")
        password = request.form.get("password")
        email = request.form.get("email") # Почта теперь тут

        if not name or not password or not email:
            return "❌ Заповни всі поля (Нік, Пошта, Пароль)"

        if name in users:
            if users[name]["password"] != password:
                return "❌ Неправильний пароль"
        else:
            users[name] = {"password": password, "email": email}
            save_users(users)

        session["name"] = name
        return redirect("/chat")
    return render_template("login.html")

@app.route("/chat")
def chat():
    if "name" not in session:
        return redirect("/")
    return render_template("index.html", name=session["name"])

users_online = {}

@socketio.on("connect")
def connect():
    name = session.get("name")
    if not name: return False
    users_online[request.sid] = name
    send({"type": "system", "msg": f"🟢 {name} приєднався"}, broadcast=True)

@socketio.on("message")
def handle_message(data):
    name = users_online.get(request.sid)
    if name:
        send({"type": "msg", "name": name, "msg": data.get("msg", "")}, broadcast=True)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)