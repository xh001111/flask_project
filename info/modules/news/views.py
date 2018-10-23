from info import db
from info.models import News, User, Comment, CommentLike
from utils.common import user_login_data
from utils.response_code import RET
from . import news_blue
from flask import render_template, abort, g, request, jsonify, current_app

# 请求路径: /news/followed_user
# 请求方式: POST
# 请求参数:user_id,action
# 返回值: errno, errmsg
@news_blue.route('/followed_user', methods=['POST'])
@user_login_data
def followed_user():
    user_id = request.json.get("user_id")
    action = request.json.get("action")

    if not all([user_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数为空")

    if not action in ["follow", "unfollow"]:
        return jsonify(errno=RET.PARAMERR, errmsg="参数为空")

    author = User.query.get(user_id)

    if not author:
        return jsonify(errno=RET.PARAMERR, errmsg="参数为空")

    if action == "follow":
        if not g.user in author.followers:
            author.followers.append(g.user)
        else:
            if  g.user in author.followers:
                author.followers.remove(g.user)

    return jsonify(errno=RET.OK, errmsg="操作成功")


# 请求路径: /news/comment_like
# 请求方式: POST
# 请求参数:comment_id,action,g.user
# 返回值: errno,errmsg
@news_blue.route('/comment_like', methods=['POST'])
@user_login_data
def comment_like():
    # 1. 判断用户是否登陆
    if not g.user:
        return jsonify(errno=RET.USERERR, errmsg="用户没登陆")
    # 2. 获取参数
    dict_data = request.json
    comment_id = dict_data.get("comment_id")
    action = dict_data.get("action")

    # 3. 判断参数是否为空
    if not all([action,comment_id]):
        return jsonify(errno=RET.NODATA, errmsg="参数为空")
    # 4. 查看操作类型
    if not action in ['add','remove']:
        return jsonify(errno=RET.NODATA, errmsg="参数为空111")
    # 5. 通过评论ID找出评论对象
    comment = Comment.query.get(comment_id)
    # 6. 判断评论对象是否存在
    if not comment:
        return jsonify(errno=RET.NODATA, errmsg="对象不存在")
    # 7. 根据操作类型点赞或者取消点赞
    try:
        if action == "add":
            comment_like = CommentLike.query.filter(CommentLike.comment_id == comment_id,CommentLike.user_id == g.user.id).first()
            if not comment_like:
                comments = CommentLike()
                comments.user_id = g.user_id
                comments.comment_id = comment_id

                db.session.add(comments)

                comment.like_count += 1
        else:
            comment_like = CommentLike.query.filter(CommentLike.comment_id == comment_id,CommentLike.user_id == g.user.id).first()
            if comment_like:
                db.session.delete(comment_like)
                if comment.like_count > 0:
                    comment.like_count -= 1
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno = RET.DBERR,errmsg = "操作失败")
    # 8. 返回状态

    return jsonify(errno=RET.OK,errmsg="操作成功")


# 请求路径: /news/news_comment
# 请求方式: POST
# 请求参数:news_id,comment,parent_id
# 返回值: errno,errmsg,评论字典
@news_blue.route('/news_comment', methods=['POST'])
@user_login_data
def news_comment():
    # 1. 判断用户是否登陆
    if not g.user:
        return jsonify(errno=RET.USERERR, errmsg="用户没登陆")
    # 2. 获取参数
    dict_data = request.json
    news_id = dict_data.get("news_id")
    content = dict_data.get("comment")
    parent_id = dict_data.get("parent_id")

    # 3. 判断参数是否为空
    if not all([news_id,content]):
        return jsonify(errno=RET.NODATA, errmsg="参数为空")
    # 4. 根据新闻编号取出新闻对象
    try:
        news = News.query.get(news_id)
    except Exception as  e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR,errmsg = "数据库操作有误")

    # 5. 判断新闻对象是否存在
    if not news:
        return jsonify(errno=RET.NODATA, errmsg="对象不存在")
    # 6. 创建评论对象,设置属性
    comment = Comment()
    comment.news_id = news_id
    comment.user_id = g.user.id
    comment.content = content
    if parent_id:
        comment.parent_id = parent_id
    # 7. 保存到数据库
    try:
        db.session.add(comment)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR,errmsg="评论失败")


    # 8. 返回响应
    return jsonify(errno=RET.OK, errmsg="返回成功",data=comment.to_dict())


@news_blue.route('/news_collect', methods=['POST'])
@user_login_data
def news_collect():
    # x. 判断用户是否登陆
    if not g.user:
        return jsonify(errno = RET.USERERR,errmsg = "用户没登陆")
    # 1. 获取参数
    dict_data = request.json
    news_id = dict_data.get("news_id")
    action = dict_data.get("action")
    # 2. 校验参数是否为空
    if not all([news_id,action]):
        return jsonify(errno = RET.NODATA,errmsg = "参数为空")

    # 3. 判断操作类型
    if not action in ["collect","cancel_collect"]:
        return jsonify(errno=RET.DATAERR, errmsg="数据类型错误")

    # 4. 根据新闻ID找到新闻对象
    try:
        news = News.query.get(news_id)
    except Exception as  e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR,errmsg = "数据库操作有误")
    # 5. 判断新闻对象是否存在
    if not news:
        return jsonify(errno=RET.NODATA,errmsg = "对象不存在")

    # 6. 根据操作类型,收藏或者取消收藏操作
    if action == "collect":
        if not news in g.user.collection_news:
            g.user.collection_news.append(news)
    else:
        if news in g.user.collection_news:
            g.user.collection_news.remove(news)

    # 7. 返回状态

    return jsonify(errno=RET.OK,errmsg = "返回成功")


@news_blue.route('/<int:news_id>')
@user_login_data
def news_detail(news_id):
    new =  News.query.get(news_id)

    if not new:
        abort(404)
    try:
        news_list = News.query.order_by(News.clicks.desc()).limit(8).all()
    except Exception as  e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR,errmsg = "数据库操作有误")


    click_news_list = []

    for click_news in news_list:
        click_news_list.append(click_news.to_dict())


    # 是否收藏新闻
    is_collected = False

    if g.user and new in g.user.collection_news:
        is_collected = True

    comments = Comment.query.filter(Comment.news_id == news_id).order_by(Comment.create_time.desc()).all()


    # 获取用户所有点赞对象
    comment_likes = []
    if g.user:
        comment_likes = g.user.comment_likes
    # 获取所有用户点赞过的评论编号
    comment_ids = []
    for comment_like in comment_likes:
        comment_ids.append(comment_like.comment_id)

    # 将评论对象列表转成字典列表
    comment_list = []

    for comment in comments:
        com_lick = comment.to_dict()

        com_lick["is_like"] = False
        # 判断用户当前是否对当前评论点过赞
        if g.user and comment.id in comment_ids:
            com_lick["is_like"] = True

        comment_list.append(com_lick)

    # 判断是否关注
    is_followed = False
    if g.user and new.user:
        if g.user in new.user.followers:
            is_followed = True



    data = {
        "news":new.to_dict(),
        "click_news_list":click_news_list,
        "user_info":g.user.to_dict() if g.user else "",
        "is_collect":is_collected,
        "comments":comment_list,
        "is_followed":is_followed

    }
    return render_template("news/detail.html",data=data)