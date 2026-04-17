import os, json
from datetime import datetime
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'gkv_chat_777'
socketio = SocketIO(app, cors_allowed_origins="*")

DATA_FILE = 'users_data.json'

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

@socketio.on('register_or_login')
def handle_auth(data):
    users = load_users()
    n = data.get('nick', '').strip()
    p = data.get('pass')
    e = data.get('email')

    # Заборона ніка "Система" або "system" (в будь-якому регістрі)
    forbidden = ["система", "system", "admin", "адмін"]
    if n.lower() in forbidden:
        return emit('auth_error', {'msg': 'Цей нікнейм заборонений!'})

    if not n or not p: return

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
    real_n = data.get('real_nick')
    msg_text = data.get('message', '').strip()

    # Команда /system для адміна
    if msg_text.startswith('/system ') and real_n == "adminkgv2015":
        sys_msg = msg_text.replace('/system ', '', 1)
        emit('message', {
            'username': '🤖 СИСТЕМА', 
            'message': sys_msg, 
            'msg_id': 'sys-' + str(datetime.now().timestamp()),
            'is_system': True 
        }, broadcast=True)
        return

    # Звичайні адмін-команди
    if msg_text.startswith('/') and real_n == "adminkgv2015":
        cmd = msg_text.split()
        if cmd[0] == "/ban" and len(cmd) > 1:
            users = load_users()
            if cmd[1] in users:
                users[cmd[1]]['banned'] = True
                save_users(users)
                emit('message', {'username': '🤖 СИСТЕМА', 'message': f'Користувач {cmd[1]} забанений!'}, broadcast=True)
        return

    data['time'] = datetime.now().strftime("%H:%M")
    emit('message', data, broadcast=True)

@socketio.on('delete_message')
def handle_delete(data):
    emit('remove_msg', {'msg_id': data['msg_id']}, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
