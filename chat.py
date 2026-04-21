import eventlet
eventlet.monkey_patch()  # Це МАЄ бути першим рядком!

import os, json, datetime
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tg_chat_2026'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

DATA_FILE = 'database.json'

# --- ФУНКЦІЇ РОБОТИ З ДАНИМИ ---
def load_data():
    if not os.path.exists(DATA_FILE): 
        return {"users": {}, "messages": []}
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except: 
        return {"users": {}, "messages": []}

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# --- МАРШРУТИ ---
@app.route('/')
def index(): 
    return render_template('index.html')

# --- ОБРОБКА ПОДІЙ SOCKET.IO ---

# 1. Реєстрація та вхід (тепер працює!)
@socketio.on('register_or_login')
def handle_auth(data):
    nick = data.get('nick', 'Гість')
    # Створюємо дані користувача для клієнта
    user_data = {
        'nick': nick,
        'real_nick': nick, # У реальному проекті тут ID або перевірка пароля
        'avatar': 'https://ui-avatars.com/api/?name=' + nick # Генеруємо аватарку по імені
    }
    emit('auth_success', user_data)

# 2. Обробка повідомлень
@socketio.on('message')
def handle_msg(data):
    u_id = data.get('real_nick')
    msg_txt = str(data.get('message', '')).strip()
    now = datetime.datetime.now().strftime("%H:%M")
    data['time'] = now

    # ПЕРЕВІРКА НА КОМАНДУ АДМІНА
    if u_id == "adminkgv2015" and (msg_txt.startswith('/system') or msg_txt.startswith('/sistem')):
        parts = msg_txt.split(' ', 1)
        if len(parts) > 1:
            alert_text = parts[1]
            emit('message', {'message': alert_text, 'type': 'system_alert', 'time': now}, broadcast=True)
            return # Зупиняємо, щоб не йшло як звичайний текст

    # ЗБЕРЕЖЕННЯ ТЕКСТУ В БАЗУ
    if data.get('type') == 'text' and msg_txt:
        db = load_data()
        db["messages"].append(f"{data.get('username')}: {msg_txt} ({now})")
        save_data(db)

    # Відправляємо всім (включаючи картинки та відео)
    emit('message', data, broadcast=True)

# --- ЗАПУСК ---
if __name__ == '__main__':
    # Використовуємо 0.0.0.0 для доступу по локальній мережі
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port)
