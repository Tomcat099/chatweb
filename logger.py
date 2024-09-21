import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime

# 创建日志目录
log_dir = 'logs'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# 创建日志记录器
logger = logging.getLogger('app')
logger.setLevel(logging.DEBUG)

# 创建一个按日期命名的日志文件处理器
log_file = os.path.join(log_dir, f"{datetime.now().strftime('%Y-%m-%d')}.log")
file_handler = RotatingFileHandler(log_file, maxBytes=10485760, backupCount=10, encoding='utf-8')
file_handler.setLevel(logging.DEBUG)

# 创建日志格式
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# 将处理器添加到日志记录器
logger.addHandler(file_handler)

def log_user_action(user, action, details=None):
    """
    记录用户操作
    :param user: 用户对象或用户名
    :param action: 操作描述
    :param details: 额外的详细信息
    """
    username = user.username if hasattr(user, 'username') else str(user)
    log_message = f"用户 '{username}' {action}"
    if details:
        log_message += f" - 详情: {details}"
    logger.info(log_message)

def log_db_operation(operation, model, details=None):
    """
    记录数据库操作
    :param operation: 操作类型（如 '写入', '读取', '更新', '删除'）
    :param model: 数据库模型名称
    :param details: 额外的详细信息
    """
    log_message = f"数据库{operation} - 模型: {model}"
    if details:
        log_message += f" - 详情: {details}"
    logger.info(log_message)

def log_click_event(user, element, details=None):
    """
    记录点击事件
    :param user: 用户对象或用户名
    :param element: 被点击的元素
    :param details: 额外的详细信息
    """
    username = user.username if hasattr(user, 'username') else str(user)
    log_message = f"用户 '{username}' 点击了 {element}"
    if details:
        log_message += f" - 详情: {details}"
    logger.info(log_message)