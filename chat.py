import os
import threading
import time
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'gkv_chat_777'
socketio = SocketIO(app, cors_allowed_origins="*")

online_users = 0

def ping_server():
    """Бот пише 'hi!', якщо нікого немає 5 хвилин, щоб Render не вимкнувся"""
    while True:
        time.sleep(300)
        if online_users == 0:
            socketio.emit('message', {'username': 'Бот-Охоронець', 'message': 'hi! Я стежу за порядком.'})

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
    # Просто пересилаємо дані (текст, фото або відео-кружечок)
    emit('message', data, broadcast=True)

@socketio.on('admin_command')
def handle_admin(data):
    cmd = data.get('command', '')
    print(f"Адмін діє: {cmd}")
    # Відповідь тільки адміну
    emit('message', {'username': 'Система', 'message': f'Команду {cmd.split()[0]} виконано приховано.'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, allow_unsafe_werkzeug=True)
