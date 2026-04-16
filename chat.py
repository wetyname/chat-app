import os
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'gkv_chat_777'
socketio = SocketIO(app, cors_allowed_origins="*")

online_users = 0

@app.route('/')
def index():
    return render_template('index.html')

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

@socketio.on('message')
def handle_msg(data):
    # Пересилаємо текст або відео всім
    emit('message', data, broadcast=True)

@socketio.on('admin_command')
def handle_admin(data):
    # Команди адміна бачиш тільки ти в консолі
    print(f"Адмін діє: {data.get('command')}")

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), allow_unsafe_werkzeug=True)
