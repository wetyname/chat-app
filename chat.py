import eventlet
eventlet.monkey_patch()

import os, datetime
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
# Збільшуємо ліміт розміру повідомлення, щоб фото пролазили без хмари
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet', max_http_buffer_size=10 * 1024 * 1024)

# Список адмінів
ADMINS = {
    "adminkgv2015": "777555111a?",
    "Tri_paloski": "999000444555a?"
    "lubly_$isi": "12130148q" 
}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('register_or_login')
def handle_auth(data):
    nick = data.get('nick', '').strip()
    password = data.get('pass', '')

    if nick == "Анонім":
        emit('auth_success', {'nick': 'Анонім', 'role': 'user'})
    elif nick in ADMINS:
        if ADMINS[nick] == password:
            emit('auth_success', {'nick': nick, 'role': 'admin'})
        else:
            emit('auth_error', {'msg': 'Невірний пароль!'})
    else:
        emit('auth_error', {'msg': 'Тільки Анонім або Адмін'})

@socketio.on('message')
def handle_msg(data):
    data['time'] = datetime.datetime.now().strftime("%H:%M")
    # Просто пересилаємо дані всім, нікуди не зберігаючи
    emit('message', data, broadcast=True)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port)
