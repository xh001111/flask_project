import logging
from logging.handlers import RotatingFileHandler

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from flask_session import Session
from config import config_dict
import redis
redis_store = None
db = SQLAlchemy()

def create_app(dict_name):
    app = Flask(__name__)
    config = config_dict.get(dict_name)
    log_file(config.LEVEL)
    app.config.from_object(config)

    CSRFProtect(app)
    # SQLAlchemy(app)
    db.init_app(app)
    Session(app)

    global redis_store
    redis_store = redis.StrictRedis(host=config.REDIS_HOST,port=config.REDIS_PORT,decode_responses=True)
    from info.modules.index import index_blue
    from info.modules.passport import image_code
    app.register_blueprint(index_blue)

    app.register_blueprint(image_code)
    print(app.url_map)
    return app

def log_file(LEVEL):
    # 设置日志的记录等级
    logging.basicConfig(level=LEVEL)  # 调试debug级
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024 * 1024 * 100, backupCount=10)
    # 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)

