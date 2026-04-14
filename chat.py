from flask import Flask, render_template, request
from flask_socketio import SocketIO, send

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'
# Ми прибираємо eventlet, щоб сервер працював стабільно
socketio = SocketIO(app, cors_allowed_origins="*")

# Списки для модерації (створюємо їх на початку)
banned_users = []
muted_users = []

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('message')
def handle_message(data):
    username = data.get('username')
    msg = data.get('message')

    if not username or not msg:
        return

    # Перевірка на бан
    if username in banned_users:
        return

    # Команди адміна (тільки для тебе)
    if username == "adminkgv2015":
        if msg.startswith('/ban '):
            name_to_ban = msg.split(' ', 1)[1].strip()
            if name_to_ban not in banned_users:
                banned_users.append(name_to_ban)
                send({'username': 'Система', 'message': f'Користувача {name_to_ban} заблоковано.'}, broadcast=True)
            return

        if msg.startswith('/mute '):
            name_to_mute = msg.split(' ', 1)[1].strip()
            if name_to_mute not in muted_users:
                muted_users.append(name_to_mute)
                send({'username': 'Система', 'message': f'Користувачу {name_to_mute} заборонено писати.'}, broadcast=True)
            return

    # Перевірка на мут
    if username in muted_users:
        return

    # Відправка звичайного повідомлення
    send(data, broadcast=True)

if __name__ == '__main__':
    # Вказуємо порт 10000, який любить Render
    socketio.run(app, host='0.0.0.0', port=10000)