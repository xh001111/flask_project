import logging

import redis


class Config(object):
    DEBUG = True
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:123456@localhost:3306/infomation15"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True

    SECRET_KEY = "aslkdjsakldjsald"
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379

    #session配置
    SESSION_TYPE = "redis"
    SESSION_USE_SIGNER = True  #标签作用
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST,port=REDIS_PORT)
    PERMANENT_SESSION_LIFETIME = 3600*2*24

    LEVEL = logging.DEBUG


# 开发人员
class DevelopConfig(Config):
    pass

# 生产配置
class ProductConfig(Config):
    DEBUG = False
    LEVEL = logging.ERROR

class TestingConfig(Config):
    TESTING = True

config_dict = {
    "develop":DevelopConfig,
    "product":ProductConfig,
    "testing":TestingConfig
}