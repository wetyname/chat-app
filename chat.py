import eventlet
eventlet.monkey_patch()
import os, json, datetime
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'nedogarky_secret'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

DB_FILE = 'database.json'

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_db(msg):
    history = load_db()
    history.append(msg)
    # Зберігаємо останні 50 повідомлень
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(history[-50:], f, ensure_ascii=False, indent=4)

@app.route('/')
def index(): 
    return render_template('index.html')

@socketio.on('connect')
def connect():
    # Відправляємо історію новому користувачу
    for msg in load_db():
        emit('message', msg)

@socketio.on('message')
def handle_msg(data):
    data['time'] = datetime.datetime.now().strftime("%H:%M")
    data['username'] = "Анонім"
    save_db(data)
    emit('message', data, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
