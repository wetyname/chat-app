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

@socketio.on('disconnect')
def disconnect():
    global online_users
    online_users -= 1
    emit('update_online', {'count': online_users}, broadcast=True)

@socketio.on('register_or_login')
def handle_auth(data):
    users = load_users()
    n, p, e = data.get('nick'), data.get('pass'), data.get('email')
    if n in users:
        if users[n]['pass'] == p: emit('auth_success', {'nick': n})
        else: emit('auth_error', {'msg': 'Невірний пароль!'})
    else:
        if not e: emit('need_email')
        else:
            users[n] = {'pass': p, 'email': e}
            save_users(users)
            emit('auth_success', {'nick': n})

@socketio.on('message')
def handle_msg(data):
    # Додаємо час відправки
    data['time'] = datetime.now().strftime("%H:%M")
    emit('message', data, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), allow_unsafe_werkzeug=True)
