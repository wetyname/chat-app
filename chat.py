import eventlet
eventlet.monkey_patch()

import os, json, datetime
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'nedogarky_secret_2026'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

@app.route('/')
def index(): 
    return render_template('index.html')

@socketio.on('register_or_login')
def handle_auth(data):
    login = data.get('nick', 'Глядач')
    
    # Якщо заходить адмін
    if login == "adminkgv2015":
        user_data = {
            'nick': "Костя (Адмін)",
            'real_nick': "adminkgv2015",
            'avatar': "⭐"
        }
    else:
        user_data = {
            'nick': "Глядач",
            'real_nick': "viewer_" + os.urandom(2).hex(),
            'avatar': "👤"
        }
    emit('auth_success', user_data)

@socketio.on('message')
def handle_msg(data):
    u_id = data.get('real_nick')
    msg_txt = str(data.get('message', '')).strip()
    now = datetime.datetime.now().strftime("%H:%M")
    data['time'] = now

    # Якщо прийшло з предложки (анонімно)
    if u_id == "anon_cloud":
        data['username'] = "Анонім"
        data['avatar'] = "☁️"
    
    # Рассылка всім користувачам
    emit('message', data, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
