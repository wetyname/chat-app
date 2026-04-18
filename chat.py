import os, json, cloudinary, cloudinary.uploader, cloudinary.api
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'gkv_secret_777'
socketio = SocketIO(app, cors_allowed_origins="*")

# --- 1. АКАУНТ ДЛЯ ФОТО ---
config_photo = {
    cloud_name="dyssbgmjc",
    api_key="293523273862564",
    api_secret="HgCd_daKzEnkavFD-PCC2ZrHwrs"
}

# --- 2. АКАУНТ ДЛЯ ВІДЕО ТА КРУЖЕЧКІВ ---
config_video = {
   "cloud_name": "dhrllrbzz",
    "api_key": "444316344877672",
    "api_secret": "wRu8t2Is2AIn3-o4PNBec0cHXVs"
}

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

# Функція очищення
def auto_clean(conf, r_type):
    try:
        cloudinary.config(**conf)
        res = cloudinary.api.resources(resource_type=r_type, max_results=100)
        # Якщо файлів більше 80, видаляємо 20 найстаріших
        if len(res['resources']) > 80:
            to_del = [r['public_id'] for r in res['resources'][-20:]]
            cloudinary.api.delete_resources(to_del, resource_type=r_type)
    except: pass

@app.route('/')
def index(): return render_template('index.html')

@socketio.on('register_or_login')
def handle_auth(data):
    users = load_users()
    n, p, e = data.get('nick'), data.get('pass'), data.get('email')
    if not n or not p: return
    display_name = "Костя Гончаров" if n == "adminkgv2015" else n
    if n in users:
        if users[n]['pass'] == p:
            ava = users[n].get('avatar', 'https://cdn-icons-png.flaticon.com/512/149/149071.png')
            emit('auth_success', {'nick': display_name, 'real_nick': n, 'avatar': ava})
        else: emit('auth_error', {'msg': 'Невірний пароль!'})
    else:
        users[n] = {'pass': p, 'email': e, 'avatar': 'https://cdn-icons-png.flaticon.com/512/149/149071.png'}
        save_users(users)
        emit('auth_success', {'nick': display_name, 'real_nick': n, 'avatar': users[n]['avatar']})

@socketio.on('send_media')
def handle_media(data):
    m_type = data['type']
    
    if m_type == 'image':
        conf, r_type, opts = config_photo, "image", {}
    else: # video або circle
        conf, r_type, opts = config_video, "video", {"resource_type": "video"}
        if m_type == 'circle':
            opts["transformation"] = [
                {"width": 400, "height": 400, "crop": "fill", "gravity": "center"},
                {"radius": "max"}
            ]

    auto_clean(conf, r_type)
    cloudinary.config(**conf)
    up = cloudinary.uploader.upload(data['file'], **opts)
    
    emit('message', {
        'username': data['username'], 'real_nick': data['real_nick'],
        'avatar': data['avatar'], 'type': m_type, 'url': up['secure_url'],
        'msg_id': "m-" + os.urandom(3).hex()
    }, broadcast=True)

@socketio.on('message')
def handle_msg(data): emit('message', data, broadcast=True)

@socketio.on('delete_message')
def handle_del(data): emit('remove_msg', data, broadcast=True)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, allow_unsafe_werkzeug=True)
