import eventlet
eventlet.monkey_patch()

import os
import datetime
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'simple_chat_key'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet', max_http_buffer_size=10 * 1024 * 1024)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('message')
def handle_msg(data):
    # Кожне повідомлення отримує ім'я "Анонім" та час
    msg_data = {
        'username': 'Анонім',
        'message': data.get('message'),
        'time': datetime.datetime.now().strftime("%H:%M")
    }
    emit('message', msg_data, broadcast=True)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port)
