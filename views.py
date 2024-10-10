from flask import Blueprint, jsonify, request, render_template, session, flash, redirect, url_for
from flask_login import login_required, current_user
from qa import generate_answer
from logger import logger, log_user_action, log_db_operation, log_click_event
from datetime import datetime
import pytz

beijing_tz = pytz.timezone('Asia/Shanghai')

main = Blueprint('main', __name__)

def init_views(db, User, History):
    @main.route('/chat/<int:user_id>')
    @login_required
    def chat(user_id):
        if current_user.id != user_id:
            flash('您没有权限访问该页面')
            log_user_action(current_user, "尝试访问未授权的聊天页面", f"目标用户ID: {user_id}")
            return redirect(url_for('main.index'))
        log_user_action(current_user, "访问了问答界面", f"用户ID: {user_id}")
        return render_template('chat.html')

    @main.route('/ask', methods=['POST'])
    @login_required
    def ask():
        try:
            data = request.json
            question = data['question']
            is_new_conversation = data.get('is_new_conversation', True)
            conversation_id = data.get('conversation_id')
            log_user_action(current_user, "提出了问题", f"问题内容: {question[:50]}...")
            
            answer = generate_answer(question)

            log_user_action(current_user, "回答了问题", f"回答内容: {answer}")
            
            if is_new_conversation or not conversation_id:
                history = History(username=current_user.username, phone=current_user.phone)
                db.session.add(history)
                db.session.flush()
                conversation_id = history.id
                log_db_operation('写入', 'History', f"新建对话 ID: {conversation_id}, 用户: {current_user.username}")
            else:
                history = History.query.get(conversation_id)
                if not history:
                    history = History(username=current_user.username, phone=current_user.phone)
                    db.session.add(history)
                    db.session.flush()
                    conversation_id = history.id
                    log_db_operation('写入', 'History', f"新建对话 ID: {conversation_id}, 用户: {current_user.username}")
                else:
                    log_db_operation('读取', 'History', f"获取对话 ID: {conversation_id}, 用户: {current_user.username}")
            
            current_conversations = history.get_conversations()
            new_conversation = {
                'question': question,
                'answer': answer,
                'timestamp': datetime.now(beijing_tz).isoformat()
            }
            current_conversations.append(new_conversation)
            history.set_conversations(current_conversations)
            
            db.session.commit()
            log_db_operation('更新', 'History', f"更新对话 ID: {conversation_id}, 用户: {current_user.username}, 新增问答数: 1")
            
            return jsonify({'answer': answer, 'conversation_id': conversation_id})
        except Exception as e:
            logger.error(f"处理问题时出错: {str(e)}", exc_info=True)
            db.session.rollback()
            log_user_action(current_user, "提问过程中遇到错误", f"错误信息: {str(e)}")
            return jsonify({'error': '处理您的请求时发生错误'}), 500

    @main.route('/get_history', methods=['GET'])
    @login_required
    def get_history():
        histories = History.query.filter_by(username=current_user.username).all()
        log_db_operation('读取', 'History', f"获取用户 {current_user.username} 的所有历史记录, 记录数: {len(histories)}")
        history_list = []
        for history in histories:
            messages = []
            conversations = history.get_conversations()
            if conversations:
                for conversation in conversations:
                    messages.append({
                        'sender': 'user', 
                        'content': conversation['question'], 
                        'timestamp': conversation.get('timestamp', '')  # 使用 get 方法，如果没有 timestamp 则返回空字符串
                    })
                    messages.append({
                        'sender': 'system', 
                        'content': conversation['answer'], 
                        'timestamp': conversation.get('timestamp', '')  # 同样使用 get 方法
                    })
                title = conversations[0]['question'][:30]
            else:
                title = "空对话"
            history_list.append({
                'id': history.id,
                'title': title,
                'messages': messages,
                'created_at': history.created_at.isoformat()
            })
        log_user_action(current_user, "获取历史对话列表", f"获取到的对话数: {len(history_list)}")
        return jsonify(history_list)

    @main.route('/delete_history/<int:history_id>', methods=['DELETE'])
    @login_required
    def delete_history(history_id):
        history = History.query.get(history_id)
        if history and history.username == current_user.username:
            db.session.delete(history)
            db.session.commit()
            log_db_operation('删除', 'History', f"删除对话 ID: {history_id}, 用户: {current_user.username}")
            log_user_action(current_user, "删除了历史对话", f"对话 ID: {history_id}")
            return jsonify({'success': True})
        log_user_action(current_user, "尝试删除不存在或未授权的历史对话", f"对话 ID: {history_id}")
        return jsonify({'success': False}), 404

    @main.route('/get_conversation/<int:history_id>', methods=['GET'])
    @login_required
    def get_conversation(history_id):
        history = History.query.get(history_id)
        if history and history.username == current_user.username:
            log_db_operation('读取', 'History', f"获取对话 ID: {history_id}, 用户: {current_user.username}")
            log_user_action(current_user, "查看了历史对话", f"对话 ID: {history_id}")
            conversations = history.get_conversations()
            messages = []
            for conversation in conversations:
                messages.append({
                    'sender': 'user', 
                    'content': conversation['question'], 
                    'timestamp': conversation.get('timestamp', '')  # 使用 get 方法，如果没有 timestamp 则返回空字符串
                })
                messages.append({
                    'sender': 'system', 
                    'content': conversation['answer'], 
                    'timestamp': conversation.get('timestamp', '')  # 同样使用 get 方法
                })
            return jsonify({'messages': messages})
        log_user_action(current_user, "尝试获取不存在或未授权的对话", f"对话 ID: {history_id}")
        return jsonify({'error': '未找到对话'}), 404

    @main.route('/log_click', methods=['POST'])
    @login_required
    def log_click():
        data = request.json
        log_click_event(current_user, data['element'], data.get('details'))
        return jsonify({'success': True})

    @main.route('/dashboard')
    @login_required
    def dashboard():
        log_user_action(current_user, "访问了个人主页")
        return render_template('dashboard.html', user=current_user)

    @main.route('/history')
    @login_required
    def history():
        histories = History.query.filter_by(username=current_user.username).all()
        log_user_action(current_user, "访问了历史对话页面", f"历史对话数量: {len(histories)}")
        log_db_operation('读取', 'History', f"获取用户 {current_user.username} 的所有历史记录, 记录数: {len(histories)}")
        return render_template('history.html', histories=histories)

    @main.route('/chat_redirect')
    def chat_redirect():
        if current_user.is_authenticated:
            log_user_action(current_user, "开始新对话")
            return redirect(url_for('main.chat', user_id=current_user.id))
        else:
            logger.info("未登录用户尝试开始新对话，重定向到登录页面")
            return redirect(url_for('auth.login', next='chat'))

    @main.route('/')
    def index():
        if current_user.is_authenticated:
            log_user_action(current_user, "访问了首页，重定向到个人主页")
            return redirect(url_for('main.dashboard'))
        logger.info("未登录用户访问首页")
        return render_template('index.html')

    @main.route('/conversation/<int:history_id>')
    @login_required
    def conversation_detail(history_id):
        history = History.query.get(history_id)
        if history and history.username == current_user.username:
            log_db_operation('读取', 'History', f"获取对话 ID: {history_id}, 用户: {current_user.username}")
            log_user_action(current_user, "查看了对话详情", f"对话 ID: {history_id}")
            conversations = history.get_conversations()
            messages = []
            for conversation in conversations:
                messages.append({
                    'sender': 'user', 
                    'content': conversation['question'], 
                    'timestamp': conversation.get('timestamp', '')  # 使用 get 方法，如果没有 timestamp 则返回空字符串
                })
                messages.append({
                    'sender': 'ai', 
                    'content': conversation['answer'], 
                    'timestamp': conversation.get('timestamp', '')
                })
            return render_template('conversation_detail.html', messages=messages)
        log_user_action(current_user, "尝试查看不存在或未授权的对话详情", f"对话 ID: {history_id}")
        flash('未找到对话或无权限查看', 'error')
        return redirect(url_for('main.history'))

    return main
