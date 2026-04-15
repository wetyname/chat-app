import sqlite3
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")


# Створюємо базу даних та таблицю, якщо її немає
def init_db():
    conn = sqlite3.connect('chat_database.db')
    cursor = conn.cursor()
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS messages
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       username
                       TEXT,
                       message
                       TEXT,
                       timestamp
                       DATETIME
                       DEFAULT
                       CURRENT_TIMESTAMP
                   )
                   ''')
    conn.commit()
    conn.close()


@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('connect')
def handle_connect():
    # Коли хтось заходить, відправляємо йому останні 50 повідомлень
    conn = sqlite3.connect('chat_database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT username, message FROM messages ORDER BY id DESC LIMIT 50')
    rows = cursor.fetchall()
    conn.close()

    # Відправляємо старі повідомлення у зворотньому порядку
    for row in reversed(rows):
        emit('message', {'username': row[0], 'message': row[1]})


@socketio.on('message')
def handle_message(data):
    # Зберігаємо нове повідомлення в базу
    conn = sqlite3.connect('chat_database.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO messages (username, message) VALUES (?, ?)',
                   (data['username'], data['message']))
    conn.commit()
    conn.close()

    # Розсилаємо повідомлення всім
    emit('message', data, broadcast=True)


if __name__ == '__main__':
    init_db()
    socketio.run(app)