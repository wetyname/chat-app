import os, json, cloudinary, cloudinary.uploader, cloudinary.api
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# --- КОНФІГУРАЦІЯ ТРЬОХ АКАУНТІВ ---

# 1. Для Фото
config_photo = {
    cloud_name="dyssbgmjc",
    api_key="293523273862564",
    api_secret="HgCd_daKzEnkavFD-PCC2ZrHwrs"
}

# 2. Для Відео (до 1 хв)
config_video = {
    "cloud_name": "NICK_VIDEO",
    "api_key": "KEY_VIDEO",
    "api_secret": "SECRET_VIDEO"
}

# 3. Для Кружечків (до 30-60 сек)
config_circle = {
    "cloud_name": "NICK_CIRCLE",
    "api_key": "KEY_CIRCLE",
    "api_secret": "SECRET_CIRCLE"
}

# Функція для швидкого очищення (видаляє найстаріші 20 файлів)
def clean_if_full(conf, res_type):
    try:
        # Підключаємось до потрібного акаунта перед перевіркою
        cloudinary.config(**conf)
        res = cloudinary.api.resources(resource_type=res_type, max_results=500)
        # Якщо файлів більше 100 (це приблизно і є межа безпеки для пам'яті)
        if len(res['resources']) > 100:
            to_del = [r['public_id'] for r in res['resources'][-20:]]
            cloudinary.api.delete_resources(to_del, resource_type=res_type)
    except: pass

@socketio.on('send_media')
def handle_media(data):
    m_type = data['type']
    file_to_up = data['file']
    
    if m_type == 'image':
        curr_conf = config_photo
        res_type = "image"
        options = {}
    elif m_type == 'video':
        curr_conf = config_video
        res_type = "video"
        options = {"resource_type": "video"}
    else: # circle
        curr_conf = config_circle
        res_type = "video"
        options = {
            "resource_type": "video",
            "transformation": [{"width": 400, "height": 400, "crop": "fill", "gravity": "center"}, {"radius": "max"}]
        }

    # Очищуємо старе перед завантаженням нового
    clean_if_full(curr_conf, res_type)
    
    # Завантажуємо на обраний акаунт
    cloudinary.config(**curr_conf)
    up = cloudinary.uploader.upload(file_to_up, **options)
    
    emit('message', {
        'username': data['username'],
        'type': m_type,
        'url': up['secure_url'],
        'avatar': data['avatar'],
        'msg_id': "m-" + os.urandom(3).hex()
    }, broadcast=True)
