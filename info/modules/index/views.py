from utils.captcha.captcha import captcha
from . import index_blue
from flask import render_template, current_app, request, jsonify,session
from info import redis_store
from info.models import User
@index_blue.route("/")
def hello_world():
    user_id = session.get("user_id")
    user = None

    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
    dict_data = {
        # 如果user存在返回左边，如果不存在返回右边
        "user_info":user.to_dict() if user else ""
    }
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

    return render_template("news/index.html",data=dict_data)




@index_blue.route('/favicon.ico')
def favicon():


    return current_app.send_static_file("news/favicon.ico")