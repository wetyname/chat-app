import os
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'gkv_chat_777'

# Налаштовуємо SocketIO для роботи в реальному часі
# allow_unsafe_werkzeug=True потрібен для стабільної роботи на Render
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def index():
    # Відкриваємо головну сторінку чату
    return render_template('index.html')

@socketio.on('message')
def handle_message(data):
    # Отримуємо повідомлення і відразу розсилаємо його ВСІМ користувачам
    # Це працює миттєво і не вимагає бази даних
    emit('message', data, broadcast=True)

@socketio.on('admin_command')
def handle_admin(data):
    # Обробка секретних команд від адміна
    cmd = data.get('command', '')
    
    # Виводимо команду в консоль сервера (її бачиш тільки ти в логах)
    print(f"Адмін виконав команду: {cmd}")
    
    # Відправляємо підтвердження ТІЛЬКИ адміну, щоб інші не бачили
    if cmd.startswith('/mute'):
        emit('message', {'username': 'Система', 'message': 'Команда MUTE активована (приховано)'})
    elif cmd.startswith('/ban'):
        emit('message', {'username': 'Система', 'message': 'Команда BAN активована (приховано)'})

if __name__ == '__main__':
    # Встановлюємо порт (5000 за замовчуванням або той, що надасть хостинг)
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, allow_unsafe_werkzeug=True)
