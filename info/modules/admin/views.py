import time
from datetime import datetime, timedelta

from flask import request, render_template, session, redirect, g, jsonify, current_app

from info import db
from info.constants import QINIU_DOMIN_PREFIX
from info.models import User, News, Category
from info.modules.admin import admin_blue
from utils.common import user_login_data
from utils.image_storage import image_storage
from utils.response_code import RET
# 37.新闻分类添加/修改
# 请求路径: /admin/add_category
# 请求方式: POST
# 请求参数: id,name
# 返回值:errno,errmsg
@admin_blue.route('/add_category', methods=['POST'])
def add_category():
    category_id = request.json.get("id")
    category_name = request.json.get("name")

    if not category_name:
        return jsonify(errno = RET.NODATA,errmsg = "参数为空")
    if category_id:
        category = Category.query.get(category_id)
        try:
            category.name = category_name
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno = RET.DATAERR,errmsg ="操作异常")

    else:
        cate = Category()

        cate.name = category_name
        try:
            db.session.add(cate)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
            return jsonify(errno = RET.DATAERR,errmsg = "数据库操作失败")



    return jsonify(errno= RET.OK ,errmsg = "返回成功")

# 36.新闻分类管理
# 请求路径: /admin/news_category
# 请求方式: GET
# 请求参数: GET,无
# 返回值:GET,渲染news_type.html页面, data数据

@admin_blue.route('/news_category')
def news_category():
    categories = Category.query.all()

    category_list = []

    for category in categories:

        category_list.append(category.to_dict())

    return render_template("admin/news_type.html",category_list=category_list)
# 35.获取/设置新闻版式编辑详情
# 请求路径: /admin/news_edit_detail
# 请求方式: GET, POST
# 请求参数: GET, news_id, POST(news_id,title,digest,content,index_image,category_id)
# 返回值:GET,渲染news_edit_detail.html页面,data字典数据,
@admin_blue.route('/news_edit_detail', methods=['GET', 'POST'])
def news_edit_detail():
    if request.method == "GET":
        # - 1.1 获取参数,新闻编号
        news_id = request.args.get("news_id")

        # - 1.2 校验参数
        if not news_id: return jsonify(errno=RET.PARAMERR, errmsg="参数不全")

        # - 1.3 根据新闻编号获取新闻对象,并判断是否存在
        try:
            news = News.query.get(news_id)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="新闻获取失败")

        if not news: return jsonify(errno=RET.NODATA, errmsg="新闻不存在")

        # 1.3.1 查询所有的分类信息
        try:
            categories = Category.query.all()
            categories.pop(0) #弹出最新
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR,errmsg="获取分类失败")

        # - 1.4 携带新闻数据,渲染页面
        return render_template("admin/news_edit_detail.html", news=news.to_dict(),categories=categories)

    news_id = request.args.get("news_id")
    title = request.args.get("title")
    digest = request.args.get("digest")
    content = request.args.get("content")
    index_image = request.args.get("index_image")
    category_id = request.args.get("category_id")

    if not all([news_id,title,digest,content,index_image,category_id]):
        return jsonify(errno = RET.NODATA,errmsg = "参数为空")

    news = News.query.get(news_id)

    if not news:
        return jsonify(errno = RET.NODATA , errmsg = "参数不存在")

    image_name = image_storage(index_image.read())

    news.title = title
    news.digest = digest
    news.content = content
    news.index_image_url = QINIU_DOMIN_PREFIX + image_name
    news.category_id = category_id

    return jsonify(errno=RET.OK, errmsg="操作成功")
# 新闻版式编辑
# 请求路径: /admin/news_edit
# 请求方式: GET
# 请求参数: GET, p, keywords
# 返回值:GET,渲染news_edit.html页面,data字典数据
@admin_blue.route('/news_edit')
def news_edit():
    page = request.args.get("p","1")
    keywords = request.args.get("keywords")
    try:
        page = int(page)
    except Exception as e:
        page = 1
    filters = []
    if keywords:
        filters.append(News.title.contains(keywords))
    paginate = News.query.filter(*filters).order_by(News.create_time.desc()).paginate(page,5,False)

    currentPage = paginate.page
    totalPage = paginate.pages
    items = paginate.items

    news_list = []

    for item in items:
        news_list.append(item)

    data = {
        "currentPage":currentPage,
        "totalPage":totalPage,
        "news_list":news_list
    }

    return render_template("admin/news_edit.html",data=data)
# 获取/设置新闻审核详情
# 请求路径: /admin/news_review_detail
# 请求方式: GET,POST
# 请求参数: GET, news_id, POST,news_id, action
# 返回值:GET,渲染news_review_detail.html页面,data字典数据
@admin_blue.route('/news_review_detail', methods=['GET', 'POST'])
def news_review_detail():
    if request.method == "GET":
        news_id = request.args.get("news_id")
        try:
            news = News.query.get(news_id)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="获取新闻失败")
        if not news:
            return jsonify(errno = RET.NODATA,errmsg = "新闻不存在")

        return render_template("admin/news_review_detail.html",news=news.to_dict())

    news_id = request.json.get("news_id")
    action = request.json.get("action")

    if not all([news_id,action]):
        return jsonify(errno = RET.NODATA, errmsg = "参数不存在")

    if not action in ["accept","reject"]:
        return jsonify(errno = RET.NODATA,errmsg = "参数错误")

    news = News.query.get(news_id)
    try:
        if action == "accept":
            news.status = 0

        else:
            reason = request.json.get("reason")

            if not reason:
                return jsonify(errno = RET.NODATA,errmsg = "原因不存在")

            news.status = -1
            news.reason = reason
            db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno = RET.DATAERR,errmsg = "出现异常")

    return jsonify(errno=RET.OK, errmsg="操作成功")
# 获取/设置新闻审核
# 请求路径: /admin/news_review
# 请求方式: GET
# 请求参数: GET, p,keywords
# 返回值:渲染user_list.html页面,data字典数据
@admin_blue.route('/news_review')
def news_review():
    page = request.args.get("p", "1")
    keywords = request.args.get("keywords")
    try:
        page = int(page)
    except Exception as e:
        page = 1
    filters = [News.status != 0]
    if keywords:
        filters.append(News.title.contains(keywords))

    paginate = News.query.filter(*filters).order_by(News.create_time.desc()).paginate(page, 5, False)
    currentPage = paginate.page
    totalPage = paginate.pages
    items = paginate.items

    new_list = []

    for item in items:
        new_list.append(item.to_review_dict())

    data = {
       "currentPage":currentPage,
        "totalPage":totalPage,
        "new_list":new_list
    }

    return render_template("admin/news_review.html",data=data)
# 31.用户列表
# 请求路径: /admin/user_list
# 请求方式: GET
# 请求参数: p
# 返回值:渲染user_list.html页面,data字典数据
@admin_blue.route('/user_list')
@user_login_data
def user_list():
    page = request.args.get("p","1")

    try:
        page = int(page)
    except Exception as e:
        page = 1
    paginate = User.query.filter(User.is_admin == False).order_by(User.create_time).paginate(page,1,False)

    currentPage = paginate.page
    totalPage = paginate.pages
    items = paginate.items
    new_list = []

    for item in items:
        new_list.append(item.to_admin_dict())

    data = {
       "currentPage":currentPage,
        "totalPage":totalPage,
        "new_list":new_list
    }
    return render_template("admin/user_list.html",data=data)
# .退出登陆
# 请求路径: /admin/logout
# 请求方式: POST
# 请求参数: 无
# 返回值:errno,errmsg

@admin_blue.route('/logout', methods=['POST'])
def logout():
    session.pop("user_id",None)
    session.pop("nick_name",None)
    session.pop("mobile",None)
    session.pop("is_admin",None)

    return jsonify(errno=RET.OK,errmsg = "退出成功")
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

    action_day = datetime.strptime(day,"%Y-%m-%d")
    end_day = datetime.now()
    day_count = User.query.filter(User.last_login >= action_day,User.last_login <= end_day,User.is_admin == False).count()

    # - 4.
    # 查询时间段内, 活跃人数
    action_date = []
    action_count = []

    for i in range(0,31):
        begin_data = action_day - timedelta(days=i)

        end_data = action_day - timedelta(days=i-1)
        action_date.append(begin_data.strftime("%Y-%m-%d"))
        every_data_count = News.query.filter(User.is_admin == False,User.last_login>=begin_data,User.last_login<=end_data).count()

        action_count.append(every_data_count)

        action_count.reverse()
        action_date.reverse()

    # 携带数据, 渲染页面
    data = {
        "day_count":day_count,
        "month_count":month_count,
        "action_user":action_user,
        "action_count":action_count,
        "action_date":action_date
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