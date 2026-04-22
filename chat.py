import eventlet
eventlet.monkey_patch()
import os, datetime
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import cloudinary
import cloudinary.uploader
from pymongo import MongoClient

app = Flask(__name__)
app.config['SECRET_KEY'] = 'nedogarky_2026'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# 1. Cloudinary налаштування
import eventlet
eventlet.monkey_patch()
import os, datetime
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import cloudinary
import cloudinary.uploader
from pymongo import MongoClient

app = Flask(__name__)
app.config['SECRET_KEY'] = 'nedogarky_2026'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# 1. Cloudinary налаштування
import eventlet
eventlet.monkey_patch()
import os, datetime
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import cloudinary
import cloudinary.uploader
from pymongo import MongoClient

app = Flask(__name__)
app.config['SECRET_KEY'] = 'nedogarky_2026'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# 1. Cloudinary налаштування
cloudinary.config( 
  cloud_name = "dhrllrbzz", 
  api_key = "444316344877672", 
  api_secret = "wRu8t2Is2AIn3-o4PNBec0cHXVs",
  secure = True
)

# 2. MongoDB налаштування (без лімітів)
MONGO_URL = "mongodb+srv://admin:<777555111>@cluster0.kfghkcq.mongodb.net/?appName=Cluster0"
client = MongoClient(MONGO_URL)
db = client['nedogarky_db']
messages_col = db['posts']

@app.route('/')
def index(): 
    return render_template('index.html')

@socketio.on('connect')
def connect():
    # Завантажуємо ВСЮ історію без ліміту
    history = list(messages_col.find().sort('_id', 1))
    for msg in history:
        msg['_id'] = str(msg['_id'])
        emit('message', msg)

@socketio.on('message')
def handle_msg(data):
    data['time'] = datetime.datetime.now().strftime("%H:%M")
    data['username'] = "Анонім"
    
    # Завантаження в хмару
    if data.get('file'):
        try:
            res = cloudinary.uploader.upload(data['file'], resource_type="auto")
            data['file'] = res['secure_url']
            data['fileType'] = res['resource_type']
        except:
            data['file'] = None

    # Збереження в базу
    messages_col.insert_one(data.copy())
    if '_id' in data: del data['_id']
    
    emit('message', data, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

# 2. MongoDB налаштування (без лімітів)
MONGO_URL = "ТВІЙ_MONGODB_CONNECTION_STRING"
client = MongoClient(MONGO_URL)
db = client['nedogarky_db']
messages_col = db['posts']

@app.route('/')
def index(): 
    return render_template('index.html')

@socketio.on('connect')
def connect():
    # Завантажуємо ВСЮ історію без ліміту
    history = list(messages_col.find().sort('_id', 1))
    for msg in history:
        msg['_id'] = str(msg['_id'])
        emit('message', msg)

@socketio.on('message')
def handle_msg(data):
    data['time'] = datetime.datetime.now().strftime("%H:%M")
    data['username'] = "Анонім"
    
    # Завантаження в хмару
    if data.get('file'):
        try:
            res = cloudinary.uploader.upload(data['file'], resource_type="auto")
            data['file'] = res['secure_url']
            data['fileType'] = res['resource_type']
        except:
            data['file'] = None

    # Збереження в базу
    messages_col.insert_one(data.copy())
    if '_id' in data: del data['_id']
    
    emit('message', data, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

# 2. MongoDB налаштування (без лімітів)
MONGO_URL = "ТВІЙ_MONGODB_CONNECTION_STRING"
client = MongoClient(MONGO_URL)
db = client['nedogarky_db']
messages_col = db['posts']

@app.route('/')
def index(): 
    return render_template('index.html')

@socketio.on('connect')
def connect():
    # Завантажуємо ВСЮ історію без ліміту
    history = list(messages_col.find().sort('_id', 1))
    for msg in history:
        msg['_id'] = str(msg['_id'])
        emit('message', msg)

@socketio.on('message')
def handle_msg(data):
    data['time'] = datetime.datetime.now().strftime("%H:%M")
    data['username'] = "Анонім"
    
    # Завантаження в хмару
    if data.get('file'):
        try:
            res = cloudinary.uploader.upload(data['file'], resource_type="auto")
            data['file'] = res['secure_url']
            data['fileType'] = res['resource_type']
        except:
            data['file'] = None

    # Збереження в базу
    messages_col.insert_one(data.copy())
    if '_id' in data: del data['_id']
    
    emit('message', data, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
