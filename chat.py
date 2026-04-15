import os
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from pymongo import MongoClient
import cloudinary
import cloudinary.uploader
from datetime import datetime

app = Flask(__name__)
# Секретний ключ для стабільної роботи SocketIO
app.config['SECRET_KEY'] = 'gkv_super_secret_123'
socketio = SocketIO(app, cors_allowed_origins="*")

# 1. НАЛАШТУВАННЯ CLOUDINARY (Впиши свої дані сюди)
cloudinary.config( 
  cloud_name = "ТВІЙ_CLOUD_NAME", 
  api_key = "ТВІЙ_API_KEY", 
  api_secret = "ТВІЙ_API_SECRET" 
)

# 2. ПІДКЛЮЧЕННЯ ДО MONGODB
MONGO_URL = "mongodb+srv://goncarovk374_db_user:HEDTIGVGEhRjRKlV@tekst.we1geml.mongodb.net/?appName=tekst"
client = MongoClient(MONGO_URL)
db = client['chat_database']
messages_col = db['messages']

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    try:
        # Завантажуємо останні 50 повідомлень
        history = list(messages_col.find().sort('_id', -1).limit(50))
        for msg in reversed(history):
            emit('message', {
                'username': msg.get('username', 'Гість'),
                'message': msg.get('message', ''),
                'image': msg.get('image', None),
                'time': msg.get('time', '')
            })
    except Exception as e:
        print(f"Помилка бази даних: {e}")

@socketio.on('message')
def handle_message(data):
    current_time = datetime.now().strftime("%H:%M")
    image_url = None

    # Перевіряємо, чи є в повідомленні картинка
    if 'image' in data and data['image']:
        try:
            # Завантажуємо в Cloudinary
            upload_result = cloudinary.uploader.upload(data['image'])
            image_url = upload_result['secure_url']
        except Exception as e:
            print(f"Помилка завантаження фото: {e}")

    # Формуємо об'єкт повідомлення
    msg_data = {
        'username': data.get('username', 'Гість'),
        'message': data.get('message', ''),
        'image': image_url,
        'time': current_time
    }
    
    # Зберігаємо в MongoDB
    try:
        messages_col.insert_one(msg_data)
    except Exception as e:
        print(f"Помилка збереження: {e}")

    # Відправляємо всім користувачам
    emit('message', msg_data, broadcast=True)

if __name__ == '__main__':
    # Налаштування порту для Render
    port = int(os.environ.get('PORT', 5000))
    # ДОДАНО allow_unsafe_werkzeug=True ЩОБ RENDER НЕ БЛОКУВАВ ЗАПУСК
    socketio.run(app, host='0.0.0.0', port=port, allow_unsafe_werkzeug=True)
