import time
from datetime import datetime

from flask import request, render_template, jsonify, session, redirect, g

from info.models import User
from info.modules.admin import admin_blue
from utils.common import user_login_data
from utils.response_code import RET
# 用户统计
# 请求路径: /admin/user_count
# 请求方式: GET
# 请求参数: 无
# 返回值:渲染页面user_count.html,字典数据
@admin_blue.route('/user_count', methods=['GET', 'POST'])
def user_count():
    # - 1.
    # 查询总人数, 不包含管理员
    action_user = User.query.filter(User.is_admin == False).count()
    # - 2.
    # 查询月活人数
    # x 获取日历对象
    calender = time.localtime()
    # 获取本月1号的时间
    month = "%d-%d-01" % (calender.tm_year,calender.tm_mon)
    # 将时间字符串转换成字符串  format = 转换成的日期格式
    action_month = datetime.strptime(month,"%Y-%m-%d")
    # 获取当前时间
    end_month = datetime.now()

    month_count = User.query.filter(User.last_login >= action_month,User.last_login <= end_month,User.is_admin == False).count()
    # - 3.
    # 查询日活人数
    day = "%d-%d-%d" % (calender.tm_year,calender.tm_mon,calender.tm_mday)

    action_day = datetime.strptime(month,"%Y-%m-%d")
    end_day = datetime.now()
    day_count = User.query.filter(User.last_login >= action_day,User.last_login <= end_day,User.is_admin == False).count()

    # - 4.
    # 查询时间段内, 活跃人数
    # - 5.
    # 携带数据, 渲染页面
    data = {
        "day_count":day_count,
        "month_count":month_count,
        "action_user":action_user
    }
    return render_template("admin/user_count.html",data=data)


# 功能描述: 管理首页
# 请求路径: /admin/index
# 请求方式: GET
# 请求参数: 无
# 返回值:渲染页面index.html,user字典数据

@admin_blue.route('/index')
@user_login_data
def index():

    admin = g.user.to_dict() if g.user else ""
    return render_template("admin/index.html",admin=admin)
# 获取/登陆,管理员登陆
# 请求路径: /admin/login
# 请求方式: GET,POST
# 请求参数:GET,无, POST,username,password
# 返回值: GET渲染login.html页面, POST,login.html页面,errmsg


@admin_blue.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == "GET":
        if session.get("is_admin"):
            return redirect("admin/index")
        return render_template("admin/login.html")
    # 1. 获取参数
    username = request.form.get("username")
    password = request.form.get("password")
    # 2. 教研参数是否为空
    if not all([username,password]):
        return render_template("admin/login.html", errmsg="管理员登陆失败")
    # 3. 根据用户 获取管理员对象

    admin = User.query.filter(User.mobile == username,User.is_admin == True).first()

    if not admin:
        return render_template("admin/login.html", errmsg="管理员不存在")

    if not admin.check_passowrd(password):
        return render_template("admin/login.html", errmsg="密码不一致")
    session["user_id"] = admin.id
    session["nick_name"] = admin.nick_name
    session["mobile"] = admin.mobile
    session["is_admin"] = True

    return redirect("/admin/index")