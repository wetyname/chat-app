import eventlet
eventlet.monkey_patch()
import datetime
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import cloudinary
import cloudinary.uploader

cloudinary.config( 
  cloud_name = "dhrllrbzz", 
  api_key = "", 
  api_secret = "",
  secure = True
)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'nedogarky_live_2026'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

@app.route('/')
def index(): 
    return render_template('index.html')

@socketio.on('message')
def handle_msg(data):
    # Кожне повідомлення отримує час та анонімний підпис
    data['time'] = datetime.datetime.now().strftime("%H:%M")
    data['username'] = "Анонім"
    # Трансляція повідомлення всім учасникам чату
    emit('message', data, broadcast=True)

if __name__ == '__main__':
    import os
    socketio.run(app, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
