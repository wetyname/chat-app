import eventlet
eventlet.monkey_patch()

import os, json, datetime, threading, time
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tg_chat_2026'
# Налаштовуємо Socket.io для надійної роботи
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

DATA_FILE = 'database.json'

def load_data():
    default = {"users": {}, "messages": []}
    if not os.path.exists(DATA_FILE):
        return default
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
            if not content: return default
            data = json.loads(content)
            if "messages" not in data: data["messages"] = []
            if "users" not in data: data["users"] = {}
            return data
    except:
        return default

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

online_count = 0

@app.route('/')
def index():
    return render_template('index.html')

def stay_awake_bot():
    while True:
        time.sleep(300)
        now = datetime.datetime.now().strftime("%H:%M")
        socketio.emit('message', {
            'username': 'Бот-Охоронець 🤖',
            'real_nick': 'bot_system',
            'message': 'Чат активний! ✨',
            'type': 'text',
            'avatar': 'https://cdn-icons-png.flaticon.com/512/4712/4712027.png',
            'time': now
        })

threading.Thread(target=stay_awake_bot, daemon=True).start()

@socketio.on('connect')
def handle_connect():
    global online_count
    online_count += 1
    emit('update_online', {'count': online_count}, broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    global online_count
    if online_count > 0: online_count -= 1
    emit('update_online', {'count': online_count}, broadcast=True)

@socketio.on('register_or_login')
def handle_auth(data):
    nick = data.get('nick', '').strip()
    pw = data.get('pass', '').strip()
    if not nick or not pw: return
    
    db = load_data()
    display_name = "Костя Гончаров" if nick == "adminkgv2015" else nick
    
    if nick in db["users"]:
        if db["users"][nick]['pass'] == pw:
            emit('auth_success', {'nick': display_name, 'real_nick': nick, 'avatar': db["users"][nick].get('avatar')})
        else:
            emit('auth_error', {'msg': 'Невірний пароль!'})
    else:
        new_user = {"pass": pw, "avatar": 'https://cdn-icons-png.flaticon.com/512/149/149071.png'}
        db["users"][nick] = new_user
        save_data(db)
        emit('auth_success', {'nick': display_name, 'real_nick': nick, 'avatar': new_user['avatar']})

@socketio.on('message')
def handle_msg(data):
    u_id = data.get('real_nick')
    msg_txt = str(data.get('message', ''))
    now = datetime.datetime.now().strftime("%H:%M")
    data['time'] = now

    if u_id == "adminkgv2015" and msg_txt.startswith('/sistem'):
        parts = msg_txt.split(' ', 1)
        if len(parts) > 1:
            emit('message', {'message': parts[1], 'type': 'system_alert', 'time': now}, broadcast=True)
            return

    if data.get('type') == 'text' and msg_txt:
        db = load_data()
        db["messages"].append(f"{data.get('username')}: {msg_txt} {now}")
        save_data(db)

    emit('message', data, broadcast=True)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port)
