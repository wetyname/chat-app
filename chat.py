import os
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from pymongo import MongoClient
import cloudinary
import cloudinary.uploader
from datetime import datetime

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# НАЛАШТУВАННЯ CLOUDINARY (впиши свої дані)
cloudinary.config( 
  cloud_name = "dyssbgmjc", 
  api_key = "293523273862564", 
  api_secret = "HgCd_daKzEnkavFD-PCC2ZrHwrs" 
)

# ПІДКЛЮЧЕННЯ ДО MONGODB
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
    
    # Якщо прийшло фото (у форматі файлу або base64)
    image_url = None
    if 'image' in data:
        upload_result = cloudinary.uploader.upload(data['image'])
        image_url = upload_result['secure_url']

    msg_data = {
        'username': data['username'],
        'message': data.get('message', ''),
        'image': image_url,
        'time': current_time
    }
    
    messages_col.insert_one(msg_data)
    emit('message', msg_data, broadcast=True)

if __name__ == '__main__':
    socketio.run(app)
