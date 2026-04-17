import os, json
from datetime import datetime
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'gkv_chat_777'
socketio = SocketIO(app, cors_allowed_origins="*")

DATA_FILE = 'users_data.json'
online_users = 0

def load_users():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            try: return json.load(f)
            except: return {}
    return {}

def save_users(users):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=4)

@app.route('/')
def index(): return render_template('index.html')

@socketio.on('connect')
def connect():
    global online_users
    online_users += 1
    emit('update_online', {'count': online_users}, broadcast=True)

@socketio.on('register_or_login')
def handle_auth(data):
    users = load_users()
    n, p, e = data.get('nick'), data.get('pass'), data.get('email')
    if not n or not p: return

    # Перевірка бану по пошті
    for u in users.values():
        if u.get('email') == e and u.get('banned'):
            return emit('auth_error', {'msg': 'Ця пошта заблокована!'})

    if n in users:
        if users[n]['pass'] == p:
            if users[n].get('banned'): return emit('auth_error', {'msg': 'Ви забанені!'})
            emit('auth_success', {'nick': n, 'real_nick': n})
        else: emit('auth_error', {'msg': 'Невірний пароль!'})
    else:
        if not e or "@" not in e: return emit('auth_error', {'msg': 'Потрібна пошта!'})
        users[n] = {'pass': p, 'email': e, 'banned': False}
        save_users(users)
        emit('auth_success', {'nick': n, 'real_nick': n})

@socketio.on('message')
def handle_msg(data):
    # Якщо повідомлення — адмін-команда, обробляємо її без розсилки в чат
    msg_text = data.get('message', '')
    if msg_text.startswith('/') and data.get('real_nick') == "adminkgv2015":
        cmd = msg_text.split()
        if cmd[0] == "/ban" and len(cmd) > 1:
            users = load_users()
            if cmd[1] in users:
                users[cmd[1]]['banned'] = True
                save_users(users)
                emit('message', {'username': 'Система', 'message': f'Користувач {cmd[1]} забанений!'}, broadcast=True)
        return

    data['time'] = datetime.now().strftime("%H:%M")
    emit('message', data, broadcast=True)

@socketio.on('delete_message')
def handle_delete(data):
    # Розсилаємо всім сигнал видалити повідомлення з конкретним ID
    emit('remove_msg', {'msg_id': data['msg_id']}, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
