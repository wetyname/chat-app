import os
import json
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'gkv_chat_777'
socketio = SocketIO(app, cors_allowed_origins="*")

# Завантаження бази користувачів
DATA_FILE = 'users_data.json'

def load_users():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=4)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('check_user')
def handle_check(data):
    users = load_users()
    nick = data.get('nick')
    # Якщо нік новий — просимо пошту
    exists = nick in users
    emit('user_status', {'exists': exists})

@socketio.on('register_or_login')
def handle_auth(data):
    users = load_users()
    nick = data.get('nick')
    pwd = data.get('pass')
    email = data.get('email')

    if nick in users:
        if users[nick]['pass'] == pwd:
            emit('auth_success', {'nick': nick, 'isAdmin': (nick == "adminkgv2015")})
        else:
            emit('auth_error', {'msg': 'Невірний пароль!'})
    else:
        # Реєстрація нового
        users[nick] = {'pass': pwd, 'email': email, 'banned': False}
        save_users(users)
        emit('auth_success', {'nick': nick, 'isAdmin': False, 'isNew': True})

@socketio.on('message')
def handle_message(data):
    emit('message', data, broadcast=True)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, allow_unsafe_werkzeug=True)
