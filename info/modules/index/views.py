from utils.captcha.captcha import captcha
from . import index_blue
from flask import render_template,current_app
from info import redis_store
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

    return render_template("news/index.html")

@index_blue.route('/img_data')
def img_data():

    name,text,image_data = captcha.generate_captcha()
    return image_data


@index_blue.route('/favicon.ico')
def favicon():


    return current_app.send_static_file("news/favicon.ico")