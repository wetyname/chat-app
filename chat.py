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


@socketio.on('connect')
def handle_connect():
    # Мы не знаем имя сразу при коннекте,
    # поэтому лучше добавить логику приветствия в сообщение
    print("Нове підключення до сервера")


# Добавь или обнови это внутри handle_message,
# чтобы при первом сообщении или входе было красиво:
@socketio.on('join')
def on_join(data):
    username = data.get('username')
    if username == "adminkgv2015":
        display_name = "Костя Гончаров"
    else:
        display_name = username

    send({'username': 'Система', 'message': f'{display_name} приєднався до чату!'}, broadcast=True)

banned_users = []
muted_users = []

# 2. Основна функція обробки повідомлень
@socketio.on('message')
def handle_message(data):
    username = data.get('username')
    msg = data.get('message')

    if not username or not msg:
        return

    # Перевірка на бан (забанений не може навіть спробувати написати)
    if username in banned_users:
        print(f"Спроба входу забаненого користувача: {username}")
        return

    # --- БЛОК АДМІНІСТРАТОРА (тільки для adminkgv2015) ---
    if username == "adminkgv2015":
        # Команда БАН: /ban Ім'я
        if msg.startswith('/ban '):
            name_to_ban = msg.split(' ', 1)[1].strip()
            if name_to_ban not in banned_users:
                banned_users.append(name_to_ban)
                print(f"АДМІН ЗАБАНЬОНИВ: {name_to_ban}")
                # Можна надіслати системне повідомлення всім
                send({'username': 'Система', 'message': f'Користувача {name_to_ban} заблоковано.'}, broadcast=True)
            return # ПОВІДОМЛЕННЯ НЕ ЙДЕ В ЧАТ (приховано)

        # Команда МУТ: /mute Ім'я
        if msg.startswith('/mute '):
            name_to_mute = msg.split(' ', 1)[1].strip()
            if name_to_mute not in muted_users:
                muted_users.append(name_to_mute)
                print(f"АДМІН ЗАМУТИВ: {name_to_mute}")
                send({'username': 'Система', 'message': f'Користувачу {name_to_mute} заборонено писати.'}, broadcast=True)
            return # ПОВІДОМЛЕННЯ НЕ ЙДЕ В ЧАТ (приховано)

    # Перевірка на мут (повідомлення просто не надсилається)
    if username in muted_users:
        return

    # 3. Надсилання звичайного повідомлення всім учасникам
    send(data, broadcast=True)

# 4. Подія підключення (українською)
@socketio.on('connect')
def handle_connect():
    print("Клієнт підключився")
    send({'username': 'Система', 'message': 'Новий користувач приєднався до чату!'}, broadcast=True)
    # Можна додати системне вітання:
    # send({'username': 'Система', 'message': 'Новий користувач приєднався до чату!'}, broadcast=True)