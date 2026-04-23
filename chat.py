import eventlet
eventlet.monkey_patch()

import os, datetime
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import cloudinary
import cloudinary.uploader
from pymongo import MongoClient

app = Flask(__name__)
app.config['SECRET_KEY'] = 'nedogarky_private_key'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# 1. НАЛАШТУВАННЯ CLOUDINARY (Встав свої дані)
cloudinary.config( 
  cloud_name = "dqih4qzpw", 
  api_key = "691998283517872", 
  api_secret = "F4wBG1D_9VDs3C44oiJFu2fOO3U",
  secure = True
)

# 2. НАЛАШТУВАННЯ MONGODB (Встав своє посилання)
# Це потрібно, щоб повідомлення на Render не видалялися
MONGO_URL = "mongodb+srv://admin:<db_password>@cluster0.kfghkcq.mongodb.net/?appName=Cluster0"
client = MongoClient(MONGO_URL)
db = client['nedogarky_database']
messages_col = db['messages']

@app.route('/')
def index(): 
    return render_template('index.html')

# Автоматичний вхід для "Аноніма"
@socketio.on('register_or_login')
def handle_auth(data):
    # Просто підтверджуємо, що система готова
    emit('auth_success')
    
    # Відразу надсилаємо ВСЮ історію повідомлень (Стрічку)
    history = list(messages_col.find().sort('_id', 1))
    for msg in history:
        msg['_id'] = str(msg['_id']) # Перетворюємо ID для JS
        emit('message', msg)

@socketio.on('message')
def handle_msg(data):
    # Додаємо час
    data['time'] = datetime.datetime.now().strftime("%H:%M")
    
    # Якщо є фото — завантажуємо в Cloudinary
    if data.get('file') and data.get('type') == 'image':
        try:
            upload_res = cloudinary.uploader.upload(data['file'], resource_type="auto")
            data['file'] = upload_res['secure_url'] # Замінюємо код на посилання
        except Exception as e:
            print(f"Помилка Cloudinary: {e}")
            data['file'] = None

    # Зберігаємо повідомлення в базу MongoDB
    messages_col.insert_one(data.copy())
    
    # Видаляємо технічний ID перед відправкою іншим
    if '_id' in data: del data['_id']
    
    # Транслюємо повідомлення всім у стрічку
    emit('message', data, broadcast=True)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port)
