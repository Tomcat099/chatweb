import os
from datetime import timedelta

class Config:
    SECRET_KEY = 'your_fixed_secret_key_here'  # 使用一个固定的密钥
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:123456@localhost:3306/chatai'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=10)  # 延长会话有效期
    UPLOAD_FOLDER = '/static/uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}