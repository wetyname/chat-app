import os
import json
import smtplib
import random
import threading
import time
from email.mime.text import MIMEText
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'gkv_chat_777'
socketio = SocketIO(app, cors_allowed_origins="*")

# НАЛАШТУВАННЯ ПОШТИ (Встав свої дані!)
SENDER_EMAIL = "твій_email@gmail.com"
SENDER_PASSWORD = "твій_пароль_додатка" 

DATA_FILE = 'users_data.json'
online_users = 0

def load_users():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=4)

def send_mail(receiver, code):
    try:
        msg = MIMEText(f"Твій код: {code}")
        msg['Subject'] = 'Підтвердження чату'
        msg['From'] = SENDER_EMAIL
        msg['To'] = receiver
        with smtplib.SMTP("smtp.gmail.com", 587) as s:
            s.starttls()
            s.login(SENDER_EMAIL, SENDER_PASSWORD)
            s.send_message(msg)
        return True
    except: return False

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
        if users[n]['pass'] == p:
            emit('auth_success', {'nick': n})
        else: emit('auth_error', {'msg': 'Невірний пароль!'})
    else:
        if not e: return emit('need_email')
        code = str(random.randint(1000, 9999))
        if send_mail(e, code):
            users[n] = {'pass': p, 'email': e, 'code': code, 'verified': False}
            save_users(users)
            emit('verify_needed', {'nick': n})
        else: emit('auth_error', {'msg': 'Помилка пошти!'})

@socketio.on('submit_code')
def handle_code(data):
    users = load_users()
    n, c = data.get('nick'), data.get('code')
    if n in users and users[n]['code'] == c:
        users[n]['verified'] = True
        save_users(users)
        emit('auth_success', {'nick': n})
    else: emit('auth_error', {'msg': 'Код невірний!'})

@socketio.on('message')
def handle_msg(data): emit('message', data, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), allow_unsafe_werkzeug=True)
