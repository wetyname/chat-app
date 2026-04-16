import os
import json
import smtplib
import random
from email.mime.text import MIMEText
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'gkv_chat_777'
socketio = SocketIO(app, cors_allowed_origins="*")

# ДАНІ ДЛЯ ВІДПРАВКИ ПОШТИ (Тут мають бути твої дані!)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "goncarovk@gmail.com" 
SENDER_PASSWORD = "твій_пароль_додатка" # Це НЕ звичайний пароль, а спеціальний код від Google

DATA_FILE = 'users_data.json'

def load_users():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=4)

def send_verification_email(receiver_email, code):
    """Функція для відправки листа через SMTP"""
    try:
        msg = MIMEText(f"Твій код підтвердження для чату: {code}")
        msg['Subject'] = 'Підтвердження реєстрації'
        msg['From'] = SENDER_EMAIL
        msg['To'] = receiver_email

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls() # Шифрування
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Помилка пошти: {e}")
        return False

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('register_or_login')
def handle_auth(data):
    users = load_users()
    nick = data.get('nick')
    pwd = data.get('pass')
    email = data.get('email')

    if nick in users:
        if users[nick]['pass'] == pwd:
            emit('auth_success', {'nick': nick})
        else:
            emit('auth_error', {'msg': 'Невірний пароль!'})
    else:
        # Створюємо код та відправляємо лист
        code = str(random.randint(1000, 9999))
        if send_verification_email(email, code):
            users[nick] = {'pass': pwd, 'email': email, 'code': code, 'verified': False}
            save_users(users)
            emit('verify_needed', {'nick': nick})
        else:
            emit('auth_error', {'msg': 'Помилка відправки листа. Перевір email!'})

@socketio.on('submit_code')
def handle_code(data):
    users = load_users()
    nick = data.get('nick')
    code = data.get('code')
    
    if nick in users and users[nick]['code'] == code:
        users[nick]['verified'] = True
        save_users(users)
        emit('auth_success', {'nick': nick})
    else:
        emit('auth_error', {'msg': 'Невірний код!'})

@socketio.on('message')
def handle_message(data):
    emit('message', data, broadcast=True)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, allow_unsafe_werkzeug=True)
2. Що змінити в index.html
Тобі потрібно додати нове вікно або поле, куди користувач вводитиме код, отриманий на пошту. Коли сервер надсилає подію verify_needed, показуй поле для коду:

JavaScript
socket.on('verify_needed', function(data) {
    let code = prompt("Введіть код підтвердження, який ми відправили на вашу пошту:");
    if(code) {
        socket.emit('submit_code', {'nick': document.getElementById('u-nick').value, 'code': code});
    }
});
