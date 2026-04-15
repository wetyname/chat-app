import os
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from pymongo import MongoClient
import cloudinary
import cloudinary.uploader
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'gkv_chat_777'
# Використовуємо звичайний режим без складних бібліотек
socketio = SocketIO(app, cors_allowed_origins="*")

# 1. ТВОЇ ДАНІ CLOUDINARY (встав свої ключі!)
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

@socketio.on('message')
def handle_message(data):
    current_time = datetime.now().strftime("%H:%M")
    img_url = None

    # Завантаження фото, якщо воно є
    if 'image' in data and data['image']:
        try:
            res = cloudinary.uploader.upload(data['image'])
            img_url = res['secure_url']
        except:
            pass

    msg_obj = {
        'username': data.get('username', 'Гість'),
        'message': data.get('message', ''),
        'image': img_url,
        'time': current_time
    }
    
    # Зберігаємо в базу та розсилаємо всім
    messages_col.insert_one(msg_obj)
    emit('message', msg_obj, broadcast=True)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    # allow_unsafe_werkzeug=True обов'язковий для Render
    socketio.run(app, host='0.0.0.0', port=port, allow_unsafe_werkzeug=True)
