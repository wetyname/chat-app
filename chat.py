import eventlet
eventlet.monkey_patch()

import os, json, datetime
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

# 1. Імпортуємо бібліотеки Cloudinary
import cloudinary
import cloudinary.uploader

app = Flask(__name__)
app.config['SECRET_KEY'] = 'nedogarky_2026_secure'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# 2. НАЛАШТУВАННЯ CLOUDINARY (Впиши свої дані сюди!)
cloudinary.config( 
  cloud_name = "dhrllrbzz", 
  api_key = "444316344877672", 
  api_secret = "wRu8t2Is2AIn3-o4PNBec0cHXVs",
  secure = True
)

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
    for msg in load_db():
        emit('message', msg)

@socketio.on('message')
def handle_msg(data):
    data['time'] = datetime.datetime.now().strftime("%H:%M")
    data['username'] = "Анонім"
    
    # 3. ЛОГІКА ЗАВАНТАЖЕННЯ МЕДІА
    if data.get('file'):
        try:
            # Відправляємо файл у хмару
            upload_result = cloudinary.uploader.upload(data['file'], resource_type="auto")
            
            # Замінюємо важкий код файлу на коротке посилання від Cloudinary
            data['file'] = upload_result['secure_url']
            data['fileType'] = upload_result['resource_type'] # 'image' або 'video'
        except Exception as e:
            print(f"Помилка завантаження: {e}")
            data['file'] = None

    save_db(data)
    emit('message', data, broadcast=True)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port)
