import os
import threading
import time
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'gkv_chat_777'
# Налаштування для стабільної роботи на Render
socketio = SocketIO(app, cors_allowed_origins="*")

online_users = 0

def ping_server():
    """Бот пише 'hi!', щоб сервер залишався активним"""
    while True:
        time.sleep(300) # 5 хвилин
        if online_users == 0:
            socketio.emit('message', {'username': 'Бот', 'message': 'hi! Я на варті.'})

threading.Thread(target=ping_server, daemon=True).start()

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    global online_users
    online_users += 1
    emit('update_online', {'count': online_users}, broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    global online_users
    online_users -= 1
    emit('update_online', {'count': online_users}, broadcast=True)

@socketio.on('message')
def handle_message(data):
    # Пересилаємо текст, фото або кружечок всім
    emit('message', data, broadcast=True)

@socketio.on('admin_command')
def handle_admin(data):
    # Команди бану та муту бачить тільки адмін
    cmd = data.get('command', '')
    emit('message', {'username': 'Система', 'message': f'Команду {cmd} виконано приховано.'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, allow_unsafe_werkzeug=True)
