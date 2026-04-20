import eventlet
eventlet.monkey_patch()

import os, json, datetime, threading, time
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tg_chat_2026'
socketio = SocketIO(app, cors_allowed_origins="*")

# --- РОБОТА З ФАЙЛОМ (ЗАМІСТЬ МОНГО) ---
DATA_FILE = 'database.json'

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except: pass
    return {"users": {}, "messages": []}

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# --- МОДЕРАЦІЯ ТА ОНЛАЙН ---
online_count = 0
muted_users = set()
banned_users = set()

@app.route('/')
def index():
    return render_template('index.html')

# --- БОТ ДЛЯ АКТИВНОСТІ ---
def stay_awake_bot():
    while True:
        time.sleep(300) # 5 хвилин
        now = datetime.datetime.now().strftime("%H:%M")
        bot_msg = {
            'username': 'Бот-Охоронець 🤖',
            'real_nick': 'bot_system',
            'message': 'Перевірка зв’язку! Я працюю, щоб чат не заснув. ✨',
            'type': 'text',
            'avatar': 'https://cdn-icons-png.flaticon.com/512/4712/4712027.png',
            'time': now
        }
        socketio.emit('message', bot_msg)

# Запуск бота в окремому фоновому процесі
threading.Thread(target=stay_awake_bot, daemon=True).start()

# --- ОБРОБКА ПОДІЙ ---
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
    nick = data.get('nick')
    pw = data.get('pass')
    if not nick or not pw: return
    
    if nick in banned_users:
        emit('auth_error', {'msg': 'Ви забанені!'})
        return

    db = load_data()
    display_name = "Костя Гончаров" if nick == "adminkgv2015" else nick
    
    if nick in db["users"]:
        if db["users"][nick]['pass'] == pw:
            emit('auth_success', {'nick': display_name, 'real_nick': nick, 'avatar': db["users"][nick].get('avatar')})
        else:
            emit('auth_error', {'msg': 'Невірний пароль!'})
    else:
        new_user = {
            "pass": pw, 
            "avatar": 'https://cdn-icons-png.flaticon.com/512/149/149071.png'
        }
        db["users"][nick] = new_user
        save_data(db)
        emit('auth_success', {'nick': display_name, 'real_nick': nick, 'avatar': new_user['avatar']})

@socketio.on('message')
def handle_msg(data):
    u_id = data.get('real_nick')
    msg_txt = data.get('message', '')
    
    if u_id in banned_users: return
    if u_id in muted_users and data.get('type') == 'text': return

    now = datetime.datetime.now().strftime("%H:%M")
    data['time'] = now

    # Команди адміна
    if u_id == "adminkgv2015" and str(msg_txt).startswith('/'):
        parts = msg_txt.split(' ')
        if len(parts) > 1:
            cmd = parts[0]
            target = parts[1]
            if cmd == '/ban': banned_users.add(target)
            if cmd == '/mute': muted_users.add(target)
            emit('message', {'username': 'Система', 'message': f'Команда {cmd} виконана для {target}', 'type': 'text', 'time': now}, broadcast=True)
            return

    # Збереження повідомлення у файл
    if data.get('type') == 'text':
        db = load_data()
        log_entry = f"{data['username']}: {msg_txt} {now}"
        db["messages"].append(log_entry)
        save_data(db)

    emit('message', data, broadcast=True)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port)
