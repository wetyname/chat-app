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
    p, e = data.get('pass'), data.get('email')
    
    # Заборона системних ніків
    if n.lower() in ["система", "system", "admin"]:
        return emit('auth_error', {'msg': 'Цей нікнейм заборонений!'})

    if n in users:
        if users[n]['pass'] == p:
            if users[n].get('banned'): return emit('auth_error', {'msg': 'Ви забанені!'})
            emit('auth_success', {'nick': n})
        else: emit('auth_error', {'msg': 'Невірний пароль!'})
    else:
        if not e or "@" not in e: return emit('auth_error', {'msg': 'Для нових потрібна пошта!'})
        users[n] = {'pass': p, 'email': e, 'banned': False}
        save_users(users)
        emit('auth_success', {'nick': n})

@socketio.on('message')
def handle_msg(data):
    real_n = data.get('real_nick')
    msg_text = data.get('message', '').strip()

    # Спеціальна команда /system для тебе
    if msg_text.startswith('/system ') and real_n == "adminkgv2015":
        sys_text = msg_text.replace('/system ', '', 1)
        emit('message', {
            'username': '🤖 СИСТЕМА', 
            'message': sys_text, 
            'msg_id': 'sys-' + str(datetime.now().timestamp()),
            'is_system': True,
            'avatar': 'https://cdn-icons-png.flaticon.com/512/8943/8943377.png'
        }, broadcast=True)
        return

    # Адмін-команди (бан)
    if msg_text.startswith('/') and real_n == "adminkgv2015":
        cmd = msg_text.split()
        if cmd[0] == "/ban" and len(cmd) > 1:
            users = load_users()
            if cmd[1] in users:
                users[cmd[1]]['banned'] = True
                save_users(users)
                emit('message', {'username': '🤖 СИСТЕМА', 'message': f'Юзер {cmd[1]} забанений!'}, broadcast=True)
        return

    emit('message', data, broadcast=True)

@socketio.on('delete_message')
def handle_delete(data):
    emit('remove_msg', {'msg_id': data['msg_id']}, broadcast=True)

if __name__ == '__main__':
    # ПАРАМЕТР allow_unsafe_werkzeug=True ВИПРАВЛЯЄ ПОМИЛКУ З СКРІНШОТА
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, allow_unsafe_werkzeug=True)
