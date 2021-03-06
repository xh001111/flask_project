import logging
from logging.handlers import RotatingFileHandler

from flask import Flask, render_template, g
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from flask_session import Session
from config import config_dict
from flask_wtf.csrf import generate_csrf
import redis

from utils.common import index_class, user_login_data

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
    from info.modules.passport import passport_blue
    from info.modules.news import news_blue
    from info.modules.user import user_blue
    from info.modules.admin import admin_blue
    app.register_blueprint(news_blue)
    app.register_blueprint(index_blue)
    app.register_blueprint(user_blue)
    app.register_blueprint(passport_blue)
    app.register_blueprint(admin_blue)
    app.add_template_filter(index_class,"index_class")

    @app.after_request
    def after_request(resp):
        value = generate_csrf()
        resp.set_cookie("csrf_token",value)
        return resp
    print(app.url_map)

    @app.errorhandler(404)
    @user_login_data
    def page_not_found(e):
        data = {
            "user_info":g.user.to_dict() if g.user else ""
        }
        return render_template("news/404.html",data=data)
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

