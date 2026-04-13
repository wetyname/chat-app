from flask import Flask, render_template_string, request, send_from_directory, render_template
from flask_socketio import SocketIO, emit
import json
import os
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key_123'
# Настройка для работы WebSockets на хостинге
socketio = SocketIO(app, cors_allowed_origins="*")

USER_DB = "users_data.json"
chat_history = []

# Загрузка пользователей
if os.path.exists(USER_DB):
    with open(USER_DB, "r", encoding="utf-8") as f:
        registered_users = json.load(f)
else:
    registered_users = {"adminkgv2015": {"pass": "gkv777555111a?", "email": "admin@chat.com"}}

def save_users():
    with open(USER_DB, "w", encoding="utf-8") as f:
        json.dump(registered_users, f, ensure_ascii=False)

users = {}

html = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Python Chat App</title>
    <link rel="manifest" href="/manifest.json">
    <style>
        body { margin: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #0f172a; color: white; }
        #login-box { text-align:center; margin-top:20vh; background: #1e293b; padding: 30px; border-radius: 15px; width: 300px; margin-left: auto; margin-right: auto; box-shadow: 0 4px 15px rgba(0,0,0,0.3); }
        #chat { height:calc(100vh - 80px); overflow-y:auto; padding:10px; display:flex; flex-direction:column; box-sizing: border-box; }
        .msg { padding:10px 15px; margin:5px; border-radius:15px; max-width:75%; word-wrap: break-word; position: relative; line-height: 1.4; }
        .left { background:#1e293b; align-self:flex-start; border-bottom-left-radius: 2px; }
        .right { background:#3b82f6; align-self:flex-end; border-bottom-right-radius: 2px; }
        .time { font-size: 0.7em; opacity: 0.6; display: block; margin-top: 5px; text-align: right; }
        #bottom { display:none; padding:15px; background:#1e293b; gap:10px; position: fixed; bottom: 0; width: 100%; box-sizing: border-box; align-items: center; }
        input { flex: 1; padding:12px; border-radius:25px; border:none; background: #334155; color: white; outline: none; }
        button { padding: 12px 20px; background:#3b82f6; color:white; border:none; border-radius:25px; cursor:pointer; font-weight: bold; }
        button:hover { background: #2563eb; }
    </style>
</head>
<body>

<div id="login-box">
    <h2 id="title">Вхід</h2>
    <input id="u_name" placeholder="Твоє ім'я" oninput="checkUser()"><br><br>
    <input id="u_email" placeholder="Пошта (для нових)" style="display:none;"><br>
    <input id="u_pass" type="password" placeholder="Пароль" style="display:none;"><br><br>
    <button onclick="handleAuth()">Увійти в чат</button>
</div>

<div id="app" style="display:none;">
    <div id="chat" onclick="document.getElementById('msg').focus()"></div>
    <div id="bottom">
        <input id="msg" placeholder="Повідомлення..." onkeypress="if(event.key==='Enter') sendMsg()">
        <button onclick="sendMsg()">▶</button>
    </div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
<script>
    var socket = io();
    var myName = "";

    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/sw.js');
    }

    function checkUser() {
        let name = document.getElementById("u_name").value;
        if (name.length > 2) socket.emit("check_user", {name: name});
    }

    socket.on("user_status", function(data) {
        document.getElementById("u_email").style.display = data.exists ? "none" : (document.getElementById("u_name").value === "adminkgv2015" ? "none" : "inline-block");
        document.getElementById("u_pass").style.display = "inline-block";
    });

    function handleAuth() {
        myName = document.getElementById("u_name").value;
        let email = document.getElementById("u_email").value;
        let pass = document.getElementById("u_pass").value;
        socket.emit("authenticate", {name: myName, email: email, pass: pass});
    }

    socket.on("auth_success", function() {
        document.getElementById("login-box").style.display = "none";
        document.getElementById("app").style.display = "block";
        document.getElementById("bottom").style.display = "flex";
    });

    socket.on("load_history", function(history) {
        let chat = document.getElementById("chat");
        chat.innerHTML = ""; 
        history.forEach(renderOneMsg);
    });

    socket.on("error_msg", function(txt) { alert(txt); });

    function sendMsg() {
        let input = document.getElementById("msg");
        if(input.value.trim() === "") return;
        socket.emit("message", {msg: input.value});
        input.value = "";
    }

    socket.on("render_msg", renderOneMsg);

    function renderOneMsg(data) {
        let chat = document.getElementById("chat");
        let div = document.createElement("div");
        let isMe = (data.name === myName || (myName === "adminkgv2015" && data.name === "Костя Гончаров"));
        div.className = "msg " + (isMe ? "right" : "left");
        div.innerHTML = "<b>" + data.name + "</b><br>" + data.msg + "<span class='time'>" + (data.time || "") + "</span>";
        chat.appendChild(div);
        chat.scrollTop = chat.scrollHeight;
    }
</script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/manifest.json")
def manifest():
    return {
        "name": "Python Chat",
        "short_name": "Chat",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#0f172a",
        "theme_color": "#3b82f6",
        "icons": [{"src": "https://cdn-icons-png.flaticon.com/512/5968/5968350.png", "sizes": "512x512", "type": "image/png"}]
    }

@app.route("/sw.js")
def sw():
    return "self.addEventListener('fetch', function(event) {});", 200, {'Content-Type': 'application/javascript'}

@socketio.on("check_user")
def check_user(data):
    exists = data["name"] in registered_users
    emit("user_status", {"exists": exists})

@socketio.on("authenticate")
def authenticate(data):
    name, password = data["name"], data["pass"]
    if name in registered_users:
        if registered_users[name]["pass"] == password:
            users[request.sid] = "Костя Гончаров" if name == "adminkgv2015" else name
            emit("auth_success")
            emit("load_history", chat_history)
        else:
            emit("error_msg", "Невірний пароль!")
    else:
        if name == "adminkgv2015": return
        registered_users[name] = {"pass": password, "email": data.get("email")}
        save_users()
        users[request.sid] = name
        emit("auth_success")
        emit("load_history", chat_history)

@socketio.on("message")
def handle_message(data):
    name = users.get(request.sid, "Гість")
    msg_data = {"name": name, "msg": data["msg"], "time": datetime.now().strftime("%H:%M")}
    chat_history.append(msg_data)
    if len(chat_history) > 50: chat_history.pop(0)
    emit("render_msg", msg_data, broadcast=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port, allow_unsafe_werkzeug=True)