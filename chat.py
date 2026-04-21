Звісно! Я переписав код, щоб команда /system працювала надійніше, а сервер краще розрізняв звичайні повідомлення та оголошення.

Ось оновлені версії обох частин:

1. Серверна частина (Python)
Я додав логіку зі split(), яка акуратно відокремлює команду від тексту, і переконався, що системні повідомлення не записуються як звичайний текст у базу.

Python
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

@socketio.on('message')
def handle_msg(data):
    u_id = data.get('real_nick')
    msg_txt = str(data.get('message', '')).strip()
    now = datetime.datetime.now().strftime("%H:%M")
    data['time'] = now

    # ОБРОБКА КОМАНДИ /system
    if u_id == "adminkgv2015" and (msg_txt.startswith('/system') or msg_txt.startswith('/sistem')):
        parts = msg_txt.split(' ', 1) # Розділяємо на ['/system', 'текст']
        if len(parts) > 1:
            alert_text = parts[1]
            emit('message', {'message': alert_text, 'type': 'system_alert', 'time': now}, broadcast=True)
            return # Виходимо, щоб не дублювати як текст

    # ЗБЕРЕЖЕННЯ ЗВИЧАЙНИХ ПОВІДОМЛЕНЬ
    if data.get('type') == 'text' and msg_txt:
        db = load_data()
        db["messages"].append(f"{data.get('username')}: {msg_txt} {now}")
        save_data(db)

    emit('message', data, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
