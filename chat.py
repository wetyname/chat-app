import eventlet
eventlet.monkey_patch()

import os, json, datetime
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tg_chat_2026'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

DATA_FILE = 'database.json'

def load_data():
    if not os.path.exists(DATA_FILE): return {"users": {}, "messages": []}
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except: return {"users": {}, "messages": []}

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

@app.route('/')
def index(): return render_template('index.html')

@socketio.on('register_or_login')
def handle_auth(data):
    login = data.get('nick', 'Гість')
    display_name = login
    
    # ПЕРЕВІРКА ДЛЯ ТЕБЕ:
    # Якщо логін adminkgv2015, то в чаті буде "Костя Гончаров"
    if login == "adminkgv2015":
        display_name = "Костя Гончаров"

    user_data = {
        'nick': display_name,    # Те, що бачать люди
        'real_nick': login,      # Твій технічний ID для команд
        'avatar': f'https://ui-avatars.com/api/?name={display_name}&background=random'
    }
    emit('auth_success', user_data)

@socketio.on('message')
def handle_msg(data):
    u_id = data.get('real_nick') # Використовуємо логін для перевірки прав
    msg_txt = str(data.get('message', '')).strip()
    now = datetime.datetime.now().strftime("%H:%M")
    data['time'] = now

    # Команда /system працює тільки для adminkgv2015
    if u_id == "adminkgv2015" and (msg_txt.startswith('/system') or msg_txt.startswith('/sistem')):
        parts = msg_txt.split(' ', 1)
        if len(parts) > 1:
            emit('message', {'message': parts[1], 'type': 'system_alert', 'time': now}, broadcast=True)
            return

    if data.get('type') == 'text' and msg_txt:
        db = load_data()
        db["messages"].append(f"{data.get('username')}: {msg_txt} ({now})")
        save_data(db)

    emit('message', data, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
