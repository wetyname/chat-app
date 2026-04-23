import eventlet
eventlet.monkey_patch()

import os, datetime
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import cloudinary
import cloudinary.uploader
from pymongo import MongoClient

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key_123'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# 1. CLOUDINARY (Встав свої дані)
cloudinary.config(cloud_name="NAME", api_key="KEY", api_secret="SECRET", secure=True)

# 2. MONGODB (Встав своє посилання)
MONGO_URL = "mongodb+srv://..." 
client = MongoClient(MONGO_URL)
db = client['chat_db']
messages_col = db['messages']

# 3. СПИСОК АДМІНІВ (Зміни на свої)
ADMINS = {
    "admin_yarik": "1111",
    "vlad_boss": "2222"
}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('register_or_login')
def handle_auth(data):
    nick = data.get('nick', '').strip()
    password = data.get('pass', '')

    if nick == "Анонім":
        emit('auth_success', {'nick': 'Анонім', 'role': 'user'})
    elif nick in ADMINS:
        if ADMINS[nick] == password:
            emit('auth_success', {'nick': nick, 'role': 'admin'})
        else:
            emit('auth_error', {'msg': 'Невірний пароль адміна!'})
    else:
        emit('auth_error', {'msg': 'Можна зайти тільки як Анонім або Адмін'})

    # Надсилаємо історію
    history = list(messages_col.find().sort('_id', 1).limit(50))
    for msg in history:
        msg['_id'] = str(msg['_id'])
        emit('message', msg)

@socketio.on('message')
def handle_msg(data):
    data['time'] = datetime.datetime.now().strftime("%H:%M")
    
    if data.get('file') and data.get('type') == 'image':
        res = cloudinary.uploader.upload(data['file'])
        data['file'] = res['secure_url']

    messages_col.insert_one(data.copy())
    if '_id' in data: del data['_id']
    emit('message', data, broadcast=True)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port)
