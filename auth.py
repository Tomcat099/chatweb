from flask import Blueprint, request, jsonify, render_template, url_for, redirect, flash, current_app, session
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import pytz
from logger import logger, log_user_action

beijing_tz = pytz.timezone('Asia/Shanghai')

auth = Blueprint('auth', __name__)

def init_auth(db, User):
    
    def find_user(login_id):
        return User.query.filter((User.username == login_id) | 
                                 (User.phone == login_id) | 
                                 (User.email == login_id)).first()

    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

    @auth.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('main.dashboard'))
        
        if request.method == 'POST':
            login_id = request.form.get('login_id')
            password = request.form.get('password')
            logger.info(f"Login attempt: {login_id}")
            user = find_user(login_id)
            if user and user.check_password(password):
                login_user(user, remember=True)
                session['user_id'] = user.id
                session['last_active'] = datetime.now(beijing_tz).isoformat()
                
                # 更新用户登录信息
                if not user.first_login_at:
                    user.first_login_at = datetime.now(beijing_tz)
                user.last_login_at = datetime.now(beijing_tz)
                user.login_count = (user.login_count or 0) + 1
                db.session.commit()
                
                log_user_action(user, "logged in")
                next_page = request.args.get('next')
                if next_page == 'chat':
                    return redirect(url_for('main.chat', user_id=user.id))
                return redirect(url_for('main.dashboard'))
            else:
                flash('用户名/手机号/邮箱或密码错误', 'error')
        
        # 清除可能存在的无效会话数据
        session.pop('user_id', None)
        session.pop('last_active', None)
        return render_template('login.html')

    @auth.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            username = request.form.get('username')
            phone = request.form.get('phone')
            email = request.form.get('email')
            password = request.form.get('password')
            
            if User.query.filter_by(username=username).first():
                flash('用户名已存在')
            elif User.query.filter_by(email=email).first():
                flash('邮箱已被注册')
            else:
                user = User(
                    username=username, 
                    email=email, 
                    phone=phone, 
                    avatar='/static/uploads/user.jpg'
                )
                user.set_password(password)
                db.session.add(user)
                db.session.commit()
                return redirect(url_for('auth.login'))
        return render_template('register.html')

    @auth.route('/logout')
    @login_required
    def logout():
        user = current_user
        user.last_logout_at = datetime.now(beijing_tz)
        db.session.commit()
        log_user_action(user, "logged out")
        logout_user()
        return redirect(url_for('main.index'))

    @auth.route('/delete_account')
    @login_required
    def delete_account():
        user = current_user
        logout_user()
        db.session.delete(user)
        db.session.commit()
        flash('您的账户已被成功注销')
        return redirect(url_for('auth.login'))

    @auth.route('/edit_profile', methods=['GET', 'POST'])
    @login_required
    def edit_profile():
        if request.method == 'POST':
            if 'avatar' in request.files:
                file = request.files['avatar']
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)
                    current_user.avatar = url_for('static', filename=f'uploads/{filename}')
            
            current_user.username = request.form.get('username', current_user.username)
            current_user.email = request.form.get('email', current_user.email)
            current_user.phone = request.form.get('phone', current_user.phone)
            
            db.session.commit()
            flash('个人信息更新成功')
            return redirect(url_for('auth.edit_profile'))
        
        return render_template('edit_profile.html')