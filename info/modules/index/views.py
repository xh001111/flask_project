from utils.captcha.captcha import captcha
from utils.response_code import RET
from . import index_blue
from flask import render_template, current_app, request, jsonify,session
from info import redis_store
from info.models import User, News, Category

@index_blue.route('/newslist')
def news_list():
    cid = request.args.get("cid","1")
    page = request.args.get("page","1")
    per_page = request.args.get("per_page","10")
    try:
        page = int(page)
        per_page = int(per_page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1
        per_page = 10
    try:
        filters = []
        if cid !="1":
            filters.append(News.category_id == cid)
        paginate = News.query.filter(*filters).order_by(News.create_time.desc()).paginate(page,per_page,False)
    except Exception as e :
        return jsonify(errno=RET.DBERR, errmsg="分页获取失败")
    totalPage = paginate.pages
    currentPage = paginate.page
    items = paginate.items

    newsList = []
    for item in items:
        newsList.append(item.to_dict())

    return jsonify(errno = RET.OK,errmsg="返回成功",totalPage=totalPage,currentPage=currentPage,newsList=newsList)

@index_blue.route("/")
def hello_world():

    user_id = session.get("user_id")
    user = None

    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)


    # redis_store.set("name","wangwu")
    # print(redis_store.get("name"))
    new_list = News.query.order_by(News.clicks.desc()).limit(10).all()

    click_news_list = []
    for news in new_list:
        click_news_list.append(news.to_dict())

    cotegories = Category.query.all()
    cotegory_list = []
    for cotegory in cotegories:
        cotegory_list.append(cotegory.to_dict())
    dict_data = {
        # 如果user存在返回左边，如果不存在返回右边
        "user_info": user.to_dict() if user else "",
        "click_news_list" : click_news_list,
        "categories":cotegory_list

    }
    return render_template("news/index.html",data=dict_data)




@index_blue.route('/favicon.ico')
def favicon():


    return current_app.send_static_file("news/favicon.ico")