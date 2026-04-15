import os
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from pymongo import MongoClient

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# ПІДКЛЮЧЕННЯ ДО MONGODB
# Використовуємо твій рядок підключення
MONGO_URL = "mongodb+srv://goncarovk374_db_user:HEDTIGVGEhRjRKlV@tekst.we1geml.mongodb.net/?appName=tekst"
client = MongoClient(MONGO_URL)
db = client['chat_database'] # Назва бази
messages_col = db['messages'] # Назва колекції (таблиці)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    # Завантажуємо останні 50 повідомлень з хмари
    history = list(messages_col.find().sort('_id', -1).limit(50))
    for msg in reversed(history):
        emit('message', {'username': msg['username'], 'message': msg['message']})

@socketio.on('message')
def handle_message(data):
    # Зберігаємо повідомлення в MongoDB
    messages_col.insert_one({
        'username': data['username'],
        'message': data['message']
    })
    # Розсилаємо всім
    emit('message', data, broadcast=True)

if __name__ == '__main__':
    socketio.run(app)