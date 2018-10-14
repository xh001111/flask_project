import redis


class Config(object):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql:root:123456@localhost:3306/infomation15"
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SECRET_KEY = "aslkdjsakldjsald"
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379

    #session配置
    SESSION_TYPE = "redis"
    SESSION_USE_SIGNER = True  #标签作用
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST,port=REDIS_PORT,decode_responses=True)
    PERMANENT_SESSION_LIFETIME = 3600*2*24


# 开发人员
class DevelopConfig(Config):
    pass

# 生产配置
class ProductConfig(Config):
    DEBUG = False

class TestingConfig(Config):
    TESTING = True

config_dict = {
    "develop":DevelopConfig,
    "product":ProductConfig,
    "testing":TestingConfig
}