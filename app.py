from flask import Flask, request, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_migrate import Migrate
from datetime import timedelta
import pytz
from logger import logger

beijing_tz = pytz.timezone('Asia/Shanghai')

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__, static_url_path='/static', static_folder='static')
    app.config.from_object('config.Config')
    
    # 设置会话超时时间
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_PERMANENT'] = True
    app.config['SESSION_USE_SIGNER'] = True
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=10)
    app.config['SESSION_REFRESH_EACH_REQUEST'] = True

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # 设置登录视图
    login_manager.login_view = 'auth.login'
    # login_manager.login_message = '请先登录'

    with app.app_context():
        from models import init_models
        User, History = init_models(db)
        
        from auth import auth, init_auth
        init_auth(db, User)
        app.register_blueprint(auth)

        from views import main, init_views
        init_views(db, User, History)
        app.register_blueprint(main)

    @login_manager.user_loader
    def load_user(user_id):
        User, _ = init_models(db)
        user = User.query.get(int(user_id))
        print(f"Loading user: {user}")
        if user:
            print(f"User loaded: ID={user.id}, Username={user.username}")
        else:
            print(f"No user found with ID: {user_id}")
        return user

    return app

app = create_app()

# 添加中间件来检查用户活动时间
@app.before_request
def check_user_activity():
    from flask import session
    from flask_login import current_user, logout_user
    from datetime import datetime, timedelta
    
    if current_user.is_authenticated:
        last_active = session.get('last_active')
        if last_active:
            last_active = datetime.fromisoformat(last_active)
            if datetime.now(beijing_tz) - last_active > timedelta(minutes=10):
                logout_user()
                return redirect(url_for('main.index'))
        session['last_active'] = datetime.now(beijing_tz).isoformat()

# @app.before_request
# def create_tables():
#     db.create_all()

@app.before_request
def before_request():
    print(f"Before request - Current user: {current_user}")
    print(f"Before request - Is authenticated: {current_user.is_authenticated}")
    print(f"Before request - Session: {session}")

@app.before_request
def log_request_info():
    logger.info(f"Request: {request.method} {request.url}")
    if current_user.is_authenticated:
        logger.info(f"User: {current_user.username}")

@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
    return "An error occurred", 500

@app.errorhandler(404)
def page_not_found(e):
    logger.warning(f"404 error: {request.url}")
    return "页面未找到", 404

if __name__ == '__main__':
    # 121.37.244.30
    app.run(host='0.0.0.0', port=8001, debug=True)