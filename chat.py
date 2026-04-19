import os, json
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'gkv_chat_2026'
socketio = SocketIO(app, cors_allowed_origins="*")

DATA_FILE = 'users_data.json'

def load_users():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            try: return json.load(f)
            except: return {}
    return {}

@app.route('/')
def index(): return render_template('index.html')

@socketio.on('register_or_login')
def handle_auth(data):
    users = load_users()
    n, p = data.get('nick'), data.get('pass')
    # Спрощена логіка входу
    display_name = "Костя Гончаров" if n == "adminkgv2015" else n
    emit('auth_success', {'nick': display_name, 'real_nick': n, 'avatar': 'https://cdn-icons-png.flaticon.com/512/149/149071.png'})

@socketio.on('message')
def handle_msg(data):
    # Ця функція відповідає за те, щоб повідомлення бачили всі
    emit('message', data, broadcast=True)

@socketio.on('send_media')
def handle_media(data):
    # Відправляємо файл напряму всім без хмари
    emit('message', data, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
