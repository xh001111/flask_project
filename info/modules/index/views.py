from info import redis_store
from . import index_blue
from flask import session
@index_blue.route("/")
def hello_world():

    redis_store.set("name","wangwu")

    print(redis_store.get("name"))
    # 测试redis数据

    # 测试session数据
    # session["name"] = "zhangsan"
    # print(session.get("name"))

    #
    # logging.debug("调试信息1")
    # logging.info("详细信息1")
    # logging.warning("警告信息1")
    # logging.error("错误信息1")

    return "helloworld"