from functools import wraps

from flask import session, current_app, jsonify, g


from utils.response_code import RET


def index_class(index):
    if index == 1:
        return "first"

    elif index == 2:
        return "second"

    elif index == 3:
        return "third"
    else:
        return " "

def user_login_data(func_out):
    @wraps(func_out)
    def wrapper(*args,**kwargs):
        user_id = session.get("user_id")
        user = None
        if user_id:
            try:
                from info.models import User
                user = User.query.get(user_id)
            except Exception as e:
                current_app.logger.error(e)
                return jsonify(errno=RET.DBERR,errmsg = "数据库错误")
        g.user = user
        return func_out(*args,**kwargs)

    return wrapper


# user_id = session.get("user_id")
# user = None
#
# try:
#     user = User.query.get(user_id)
# except Exception as e:
#     current_app.logger.error(e)
#     return jsonify(errno=RET.DBERR,errmsg = "数据库错误")
