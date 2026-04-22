import eventlet
eventlet.monkey_patch()
import os, datetime
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

# Бібліотеки для хмар
import cloudinary
import cloudinary.uploader
from pymongo import MongoClient

app = Flask(__name__)
app.config['SECRET_KEY'] = 'nedogarky_render_2026'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# 1. Налаштування Cloudinary
cloudinary.config( 
  cloud_name = "dhrllrbzz", 
  api_key = "444316344877672", 
  api_secret = "wRu8t2Is2AIn3-o4PNBec0cHXVs",
  secure = True
)

# 2. Налаштування MongoDB (замість database.json)
MONGO_URL = "mongodb+srv://admin:<777555111>@cluster0.kfghkcq.mongodb.net/?appName=Cluster0"
client = MongoClient(MONGO_URL)
db = client['podslushano_db']
messages_col = db['messages']

@app.route('/')
def index(): 
    return render_template('index.html')

@socketio.on('connect')
def connect():
    # Завантажуємо історію з MongoDB (останні 50 повідомлень)
    history = list(messages_col.find().sort('_id', 1)
    for msg in history:
        msg['_id'] = str(msg['_id']) # Прибираємо технічне поле MongoDB
        emit('message', msg)

@socketio.on('message')
def handle_msg(data):
    data['time'] = datetime.datetime.now().strftime("%H:%M")
    data['username'] = "Анонім"
    
    # Завантаження файлу в Cloudinary
    if data.get('file'):
        try:
            upload_result = cloudinary.uploader.upload(data['file'], resource_type="auto")
            data['file'] = upload_result['secure_url']
            data['fileType'] = upload_result['resource_type']
        except Exception as e:
            print(f"Cloudinary Error: {e}")
            data['file'] = None

    # Зберігаємо в MongoDB (воно не видалиться на Render)
    messages_col.insert_one(data.copy())
    
    # Видаляємо дані з бази перед розсилкою, щоб не слати зайвого
    if '_id' in data: del data['_id']
    
    emit('message', data, broadcast=True)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port)
