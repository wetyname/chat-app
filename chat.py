import os, json, cloudinary, cloudinary.uploader
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'gkv_chat_777'
socketio = SocketIO(app, cors_allowed_origins="*")

# Налаштування Cloudinary
cloudinary.config(
    cloud_name="dyssbgmjc",
    api_key="293523273862564",
    api_secret="HgCd_daKzEnkavFD-PCC2ZrHwrs"
)

DATA_FILE = 'users_data.json'

def load_users():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            try: return json.load(f)
            except: return {}
    return {}

def save_users(users):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=4)

@app.route('/')
def index(): return render_template('index.html')

@socketio.on('register_or_login')
def handle_auth(data):
    users = load_users()
    n, p = data.get('nick'), data.get('pass')
    if not n or not p: return
    display_name = "Костя Гончаров" if n == "adminkgv2015" else n
    if n in users:
        if users[n]['pass'] == p:
            ava = users[n].get('avatar', 'https://cdn-icons-png.flaticon.com/512/149/149071.png')
            emit('auth_success', {'nick': display_name, 'real_nick': n, 'avatar': ava})
        else: emit('auth_error', {'msg': 'Невірний пароль!'})
    else:
        users[n] = {'pass': p, 'avatar': 'https://cdn-icons-png.flaticon.com/512/149/149071.png'}
        save_users(users)
        emit('auth_success', {'nick': display_name, 'real_nick': n, 'avatar': users[n]['avatar']})

@socketio.on('update_avatar')
def update_avatar(data):
    users = load_users()
    real_n = data.get('real_nick')
    if real_n in users:
        up = cloudinary.uploader.upload(data.get('avatar'))
        url = up['secure_url']
        users[real_n]['avatar'] = url
        save_users(users)
        emit('avatar_changed', {'avatar': url, 'real_nick': real_n}, broadcast=True)

@socketio.on('upload_music')
def handle_music(data):
    # resource_type="video" потрібен для аудіофайлів у Cloudinary
    up = cloudinary.uploader.upload(data['file'], resource_type="video")
    url = up['secure_url']
    emit('play_music', {'url': url}, broadcast=True)

@socketio.on('message')
def handle_msg(data):
    emit('message', data, broadcast=True)

@socketio.on('delete_message')
def handle_del(data):
    emit('remove_msg', data, broadcast=True)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, allow_unsafe_werkzeug=True)
