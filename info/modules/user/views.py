from sqlalchemy.sql.functions import user

from info import constants, db
from info.models import Category, News, User
from utils.common import user_login_data
from utils.image_storage import image_storage
from utils.response_code import RET
from . import user_blue
from flask import render_template, g, redirect, request, jsonify, current_app


# 获取其他用户,新闻列表
# 请求路径: /user/other_news_list
# 请求方式: GET
# 请求参数:p,user_id
# 返回值: errno,errmsg
@user_blue.route('/other_news_list')
def other_news_list():
    # 1. 获取参数
    page = request.args.get("p","1")
    user_id = request.args.get("user_id")
    # 2. 判断参数是否为空 转换参数
    if not all([page,user_id]):
        return jsonify(errno=RET.PARAMERR,errmsg = "参数为空")
    try:
        page = int(page)
    except Exception as e:
        page = 1
    # 3. 查询用户对象 取出对象

    author = User.query.get(user_id)
    # 4. 分页查询
    paginate = author.news_list.order_by(News.create_time.desc()).paginate(page,2,False)
    # 5. 获取分页对象属性,总页数,当前页,当前页对象列表
    currentPage = paginate.page
    totlePage = paginate.pages
    items = paginate.items

    news_list = []
    for item in items:
        news_list.append(item.to_dict())
    # 6. 渲染页面
    data = {
        "currentPage":currentPage,
        "totlePage":totlePage,
        "news_list":news_list
    }
    return jsonify(errno=RET.OK,errmsg = "返回成功",data=data)
# 其他用户界面
# 请求路径: /user/other
# 请求方式: GET
# 请求参数:id
# 返回值: 渲染other.html页面,字典data数据

@user_blue.route('/other')
@user_login_data
def other():
    author_id = request.args.get("id")
    if not author_id:
        return jsonify(errno=RET.PARAMERR,errmsg = "参数为空")

    author = User.query.get(author_id)

    if not author:
        return jsonify(errno=RET.NODATA,errmsg = "用户不存在")

    is_followed = False
    # 判断登陆的用户,是否有关注该作者
    if g.user:
        if g.user in author.followers:
            is_followed = True

    data = {
        "is_followed":is_followed,
        "user_info":g.user.to_dict() if g.user else "",
        "author":author.to_dict()
    }

    return render_template("news/other.html",data=data)
# 请求路径: /user/user_follow
# 请求方式: GET
# 请求参数:p
# 返回值: 渲染user_follow.html页面,字典data数据
@user_blue.route('/user_follow')
@user_login_data
def user_follow():
    page = request.args.get("p","1")

    try:
        page = int(page)
    except Exception as e :
        page = 1
    # 获取该用户关注的对象
    paginate = g.user.followed.paginate(page,2,False)

    totalpage = paginate.pages
    currentpage = paginate.page
    items = paginate.items

    items_list = []

    for item in items:
        items_list.append(item.to_dict())

    data = {
        "totalpage":totalpage,
        "currentpage":currentpage,
        "items_list":items_list
    }


    return render_template("news/user_follow.html",data=data)

# .用户新闻列表
# 请求路径: /user/news_list
# 请求方式:GET
# 请求参数:p
# 返回值:GET渲染user_news_list.html页面
@user_blue.route('/news_list')
@user_login_data
def news_list():
    page = request.args.get("p","1")

    try:
        page = int(page)
    except Exception as e:
        page = 1

    paginate = News.query.filter(News.user_id == g.user.id).order_by(News.create_time.desc()).paginate(page,2,False)

    totalPage = paginate.pages
    currentPage = paginate.page
    items = paginate.items
    news_list = []
    for item in items:
        news_list.append(item.to_review_dict())

    data = {
        "totalPage":totalPage,
        "currentPage":currentPage,
        "news_list":news_list
    }
    return  render_template("news/user_news_list.html",data=data)


# 获取/设置,新闻发布
# 请求路径: /user/news_release
# 请求方式:GET,POST
# 请求参数:GET无, POST ,title, category_id,digest,index_image,content
# 返回值:GET请求,user_news_release.html, data分类列表字段数据,

@user_blue.route('/news_release', methods=['GET', 'POST'])
@user_login_data
def news_release():
    if request.method == "GET":
        category = Category.query.all()
        category.pop(0)
        return render_template("news/user_news_release.html",category=category)

    title = request.form.get("title")
    category_id = request.form.get("category_id")
    digest = request.form.get("digest")
    index_image = request.files.get("index_image")
    content = request.form.get("content")

    if not all([title,category_id,digest,index_image,content]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")

    image_name = image_storage(index_image.read())

    if not image_name:
        return jsonify(errno=RET.NODATA, errmsg="上传失败")

    news = News()
    news.title = title
    news.source = g.user.nick_name
    news.category_id = category_id
    news.digest = digest
    news.index_image_url = constants.QINIU_DOMIN_PREFIX + image_name
    news.content = content
    news.user_id = g.user.id
    news.status = 1
    try:
        db.session.add(news)
        db.session.commit()
    except Exception as e:

        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR,errmsg = "发布失败")

    return jsonify(errno=RET.OK, errmsg="新闻发布成功")



# 请求路径: /user/ collection
# 请求方式:GET
# 请求参数:p(页数)
# 返回值: user_collection.html页面
@user_blue.route('/collection')
@user_login_data
def collection():

    page = request.args.get("p","1")

    try:
        page = int(page)
    except Exception as e:
        page = 1

    paginate = g.user.collection_news.paginate(page,2,False)

    totalPage = paginate.pages
    currentPage = paginate.page
    items = paginate.items
    paginate_list = []
    for item in items:
        paginate_list.append(item.to_dict())

    data = {
        "totalPage":totalPage,
        "currentPage":currentPage,
        "paginate_list":paginate_list
    }
    return render_template("news/user_collection.html",data=data)
# 获取/设置,用户头像上传
# 请求路径: /user/pic_info
# 请求方式:GET,POST
# 请求参数:无, POST有参数,avatar
# 返回值:GET请求: user_pci_info.html页面,data字典数据, POST请求: errno, errmsg,avatar_url
@user_blue.route('/pic_info', methods=['GET', 'POST'])
@user_login_data
def pic_info():
    if request.method == "GET":
        return render_template("news/user_pic_info.html",user=g.user.to_dict())

    avatar = request.files.get("avatar")

    if not avatar:
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")
    try:
        image_name = image_storage(avatar.read())
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="操作失败")

    if not image_name:
        return jsonify(errno=RET.NODATA,errmsg = "上传失败")

    g.user.avatar_url = image_name

    data = {
        "avatar_url":constants.QINIU_DOMIN_PREFIX + image_name
    }

    return jsonify(errno=RET.OK,errmsg="返回成功",data=data)


# 请求路径: /user/pass_info
# 请求方式:GET,POST
# 请求参数:GET无, POST有参数,old_password, new_password
# 返回值:GET请求: user_pass_info.html页面,data字典数据, POST请求: errno, errmsg

@user_blue.route('/pass_info', methods=['GET', 'POST'])
@user_login_data
def pass_info():
    if request.method == "GET":
        return render_template("news/user_pass_info.html",user=g.user.to_dict())

    old_password = request.json.get("old_password")
    new_password = request.json.get("new_password")

    if not all([old_password,new_password]):
        return jsonify(errno=RET.PARAMERR,errmsg = "参数不全")

    if not g.user.check_passowrd(old_password):
        return jsonify(errno = RET.PARAMERR, errmsg = "密码不正确")
    g.user.password = new_password

    return jsonify(errno = RET.OK,errmsg = "返回成功")



# 获取/设置用户基本信息
# 请求路径: /user/base_info
# 请求方式:GET,POST
# 请求参数:POST请求有参数,nick_name,signature,gender
# 返回值:errno,errmsg
@user_blue.route('/base_info', methods=['GET', 'POST'])
@user_login_data
def base_info():

    if request.method == "GET":

        return render_template("news/user_base_info.html",user=g.user.to_dict())
    nick_name = request.json.get("nick_name")
    signature = request.json.get("signature")
    gender = request.json.get("gender")

    if not all([signature,nick_name,gender]):
        return jsonify(errno=RET.PARAMERR,errmsg = "参数不全")
    try:
        g.user.nick_name = nick_name
        g.user.signature = signature
        g.user.gender = gender

    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR,errmsg = "数据库操作异常")

    return jsonify(errno = RET.OK,errmsg = "返回成功")

#展示个人中心页面
# 请求路径: /user/info
# 请求方式:GET
# 请求参数:无
# 返回值: user.html页面,用户字典data数据
@user_blue.route('/info')
@user_login_data
def user_index():

    #判断用户是否登陆了
    if not g.user:
        return redirect("/")

    #拼接数据,返回页面
    data = {
        "user_info": g.user.to_dict()
    }

    return render_template("news/user.html",data=data)