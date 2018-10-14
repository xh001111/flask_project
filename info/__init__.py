from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from flask_session import Session
from config import config_dict
import redis
def create_app(dict_name):
    app = Flask(__name__)
    config = config_dict[dict_name]

    app.config.from_object(config)
    Session(app)
    CSRFProtect(app)
    SQLAlchemy(app)
    redis.StrictRedis(host=config.REDIS_HOST,port=config.REDIS_PORT,decode_responses=True)
    return app

