from flask_login import UserMixin
import bcrypt
import json
from datetime import datetime
import pytz

beijing_tz = pytz.timezone('Asia/Shanghai')

def init_models(db):
    if 'User' not in db.Model.registry._class_registry:
        class User(UserMixin, db.Model):
            __tablename__ = 'user'
            id = db.Column(db.Integer, primary_key=True)
            username = db.Column(db.String(80), unique=True, nullable=False)
            phone = db.Column(db.String(20), unique=True, nullable=False)
            email = db.Column(db.String(120), unique=True, nullable=False)
            password_hash = db.Column(db.String(255))
            avatar = db.Column(db.String(255), default='/static/uploads/user.jpg')
            
            # 修改时间字段
            created_at = db.Column(db.DateTime, default=lambda: datetime.now(beijing_tz))
            first_login_at = db.Column(db.DateTime)
            last_login_at = db.Column(db.DateTime)
            login_count = db.Column(db.Integer, default=0)
            is_active = db.Column(db.Boolean, default=True)

            def set_password(self, password):
                self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

            def check_password(self, password):
                return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

    if 'History' not in db.Model.registry._class_registry:
        class History(db.Model):
            __tablename__ = 'history'
            __table_args__ = {'extend_existing': True}
            id = db.Column(db.Integer, primary_key=True)
            username = db.Column(db.String(80), nullable=False)
            phone = db.Column(db.String(20), nullable=False)
            conversations = db.Column(db.Text, nullable=True)
            created_at = db.Column(db.DateTime, default=lambda: datetime.now(beijing_tz))

            def get_conversations(self):
                return json.loads(self.conversations) if self.conversations else []

            def set_conversations(self, conversations):
                self.conversations = json.dumps(conversations) if conversations else None

            def __repr__(self):
                return f'<History {self.id}>'

    return db.Model.registry._class_registry.get('User'), db.Model.registry._class_registry.get('History')