import os, json, threading
from datetime import datetime
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'gkv_chat_777'
socketio = SocketIO(app, cors_allowed_origins="*")

DATA_FILE = 'users_data.json'
online_users = 0
muted_users = {} # Список тих, хто не може писати

def load_users():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            try: return json.load(f)
            except: return {}
    return {}

def save_users(users):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=4)

@app.route('/')
def index(): return render_template('index.html')

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

@socketio.on('register_or_login')
def handle_auth(data):
    users = load_users()
    n, p, e = data.get('nick'), data.get('pass'), data.get('email')
    
    if n in users and users[n].get('banned'):
        return emit('auth_error', {'msg': 'Ви забанені на цьому сервері!'})
        
    display_name = "Костя Гончаров" if n == "adminkgv2015" else n
    if n in users:
        if users[n]['pass'] == p: emit('auth_success', {'nick': display_name, 'real_nick': n})
        else: emit('auth_error', {'msg': 'Невірний пароль!'})
    else:
        if not e: emit('need_email')
        else:
            users[n] = {'pass': p, 'email': e, 'banned': False}
            save_users(users)
            emit('auth_success', {'nick': display_name, 'real_nick': n})

@socketio.on('message')
def handle_msg(data):
    user = data.get('username')
    real_n = data.get('real_nick') # Використовуємо реальний нік для перевірок
    
    # Перевірка на мут
    if real_n in muted_users:
        return emit('message', {'username': 'Система', 'message': 'Ви не можете писати, у вас мут!', 'time': ''})

    data['time'] = datetime.now().strftime("%H:%M")
    emit('message', data, broadcast=True)

# --- АДМІН КОМАНДИ ---
@socketio.on('admin_cmd')
def admin_cmd(data):
    if data.get('admin') != "adminkgv2015": return
    
    cmd = data.get('cmd').split() # Розбиваємо команду на частини
    users = load_users()
    action = cmd[0] # /ban, /mute, /tban
    target = cmd[1] if len(cmd) > 1 else ""

    if action == "/ban" and target in users:
        users[target]['banned'] = True
        save_users(users)
        emit('message', {'username': 'Система', 'message': f'Користувач {target} забанений назавжди!'}, broadcast=True)
        
    elif action == "/mute" and target:
        muted_users[target] = True
        emit('message', {'username': 'Система', 'message': f'Користувачу {target} заборонено писати!'}, broadcast=True)

    elif action == "/tban" and len(cmd) > 2:
        sec = int(cmd[2])
        muted_users[target] = True
        emit('message', {'username': 'Система', 'message': f'{target} замучений на {sec} сек!'}, broadcast=True)
        # Таймер розблокування
        threading.Timer(sec, lambda: muted_users.pop(target, None)).start()

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), allow_unsafe_werkzeug=True)
