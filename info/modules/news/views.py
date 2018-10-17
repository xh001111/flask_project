from info.models import News, User
from . import news_blue
from flask import render_template, abort, session, current_app


@news_blue.route('/<int:news_id>')
def news_detail(news_id):
    news =  News.query.get(news_id)

    if not news:
        abort(404)

    news_list = News.query.order_by(News.clicks.desc()).limit(8).all()

    click_news_list = []

    for news in news_list:
        click_news_list.append(news.to_dict())

    #获取用户数据
    #获取用户的编号,从session
    user_id = session.get("user_id")

    #判断用户是否存在
    user = None
    if user_id:
        try:
            user = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)
    data = {
        "news":news.to_dict(),
        "click_news_list":click_news_list,
        "user":user.to_dict() if user else ""
    }
    return render_template("news/detail.html",data=data)