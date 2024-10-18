app.py（主启动文件）
config.py（配置文件）
models.py（数据库模型）
auth.py（认证相关路由和函数）
qa.py（问答推理模块）
views.py（其他视图函数）
utils.py（工具函数）

# 首次使用要输入下面的三条命令
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# 安装MySQL
docker-compose pull
docker-compose up -d        # 后台启动
docker-compose restart      # 重启
docker-compose down         # 停止服务
docker-compose ps           # 查看服务状态
docker-compose logs -f      # 查看日志服务

# 服务器后台启动
nohup python app.py > output.log 2>&1 &
ps aux | grep app.py


