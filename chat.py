import os
import threading
import time
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'gkv_chat_777'
socketio = SocketIO(app, cors_allowed_origins="*")

# Змінна для підрахунку людей в мережі
online_users = 0

def ping_server():
    """Функція, яка пише в чат, якщо нікого немає, щоб сервер не заснув"""
    global online_users
    while True:
        # Чекаємо 5 хвилин (300 секунд)
        time.sleep(300)
        if online_users == 0:
            # Надсилаємо повідомлення від імені бота
            socketio.emit('message', {'username': 'Бот-Охоронець', 'message': 'hi! Сервер працює.'})
            print("Сервер активований ботом, бо в мережі 0 людей.")

# Запускаємо "будильник" в окремому потоці
threading.Thread(target=ping_server, daemon=True).start()

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    global online_users
    online_users += 1
    # Повідомляємо всіх про кількість людей
    emit('update_online', {'count': online_users}, broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    global online_users
    online_users -= 1
    emit('update_online', {'count': online_users}, broadcast=True)

@socketio.on('message')
def handle_message(data):
    emit('message', data, broadcast=True)

@socketio.on('admin_command')
def handle_admin(data):
    cmd = data.get('command', '')
    if cmd.startswith('/mute') or cmd.startswith('/ban'):
        emit('message', {'username': 'Система', 'message': 'Команда виконана (приховано)'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, allow_unsafe_werkzeug=True)
