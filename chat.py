import eventlet
eventlet.monkey_patch()

import os, json, datetime
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from pymongo import MongoClient

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tg_chat_2026'
socketio = SocketIO(app, cors_allowed_origins="*")

# --- MONGODB CONFIG ---
# Встав своє посилання замість цього:
MONGO_URL = "mongodb+srv://admin:<777555111>@cluster0.kfghkcq.mongodb.net/?appName=Cluster0"
client = MongoClient(MONGO_URL)
db = client['chat_db']
messages_col = db['messages']
users_col = db['users']

online_count = 0
muted_users = set()
banned_users = set()

@app.route('/')
def index(): return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    global online_count
    online_count += 1
    emit('update_online', {'count': online_count}, broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    global online_count
    online_count -= 1
    emit('update_online', {'count': online_count}, broadcast=True)

@socketio.on('register_or_login')
def handle_auth(data):
    n = data.get('nick')
    if n in banned_users:
        emit('auth_error', {'msg': 'Ви забанені!'})
        return
    
    user = users_col.find_one({"nick": n})
    display_name = "Костя Гончаров" if n == "adminkgv2015" else n
    
    if user:
        if user['pass'] == data.get('pass'):
            emit('auth_success', {'nick': display_name, 'real_nick': n, 'avatar': user.get('avatar')})
        else: emit('auth_error', {'msg': 'Невірний пароль!'})
    else:
        new_user = {"nick": n, "pass": data.get('pass'), "email": data.get('email'), "avatar": 'https://cdn-icons-png.flaticon.com/512/149/149071.png'}
        users_col.insert_one(new_user)
        emit('auth_success', {'nick': display_name, 'real_nick': n, 'avatar': new_user['avatar']})

@socketio.on('message')
def handle_msg(data):
    u_id = data.get('real_nick')
    msg_txt = data.get('message', '')
    
    if u_id in banned_users: return
    if u_id in muted_users and data.get('type') == 'text': return

    now = datetime.datetime.now().strftime("%H:%M")
    data['time'] = now

    # Адмін команди
    if u_id == "adminkgv2015" and msg_txt.startswith('/'):
        p = msg_txt.split(' ')
        if len(p) > 1:
            if p[0] == '/ban': banned_users.add(p[1])
            if p[0] == '/mute': muted_users.add(p[1])
            emit('message', {'username': 'Система', 'message': f'Команда {p[0]} виконана для {p[1]}', 'type': 'text', 'time': now}, broadcast=True)
            return

    # Збереження в хмару (MongoDB)
    if data.get('type') == 'text':
        log = f"{data['username']}: {msg_txt} {now}"
        messages_col.insert_one({"log": log, "time": now, "user": data['username']})

    emit('message', data, broadcast=True)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port)
