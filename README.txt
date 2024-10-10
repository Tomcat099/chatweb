app.py（主启动文件）
config.py（配置文件）
models.py（数据库模型）
auth.py（认证相关路由和函数）
qa.py（问答推理模块）
views.py（其他视图函数）
utils.py（工具函数）

# 第二次修改,增加来自被人的问答数据及推理脚本
./data      # 数据集文件
./dict      # 字典文件
./prepare_data/datasoider.py      # 网络资讯采集脚本
./prepare_data/datasoider.py      # 网络资讯采集脚本
./prepare_data/max_cut.py         # 基于词典的最大向前/向后切分脚本

build_medicalgraph.py       # 知识图谱入库脚本 
chatbot_graph.py            # 问答程序脚本
answer_search.py            # 
question_classifier.py      # 问句类型分类脚本
question_parser.py          # 问句解析脚本



# 首次使用要输入下面的三条命令
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# 服务器后台启动
nohup python app.py > output.log 2>&1 &
ps aux | grep app.py


