from flask.json import jsonify

from info.libs.yuntongxun.sms import CCP
from utils.captcha.captcha import captcha
from utils.response_code import RET
from . import passport_blue
from flask import request, current_app, make_response, json, session
from info import redis_store, constants, db
import re
import random
from info.models import  User
# 退出用户
@passport_blue.route('/logout', methods=['POST'])
def logout():
    session.pop("user_id",None)
    session.pop("nick_name",None)
    session.pop("mobile",None)

    return jsonify(erron=RET.OK,errmsg = "退出成功")

# 登陆用户
@passport_blue.route('/login', methods=['POST'])
def login():
    # 1. 接受参数
    dict_data = request.json
    mobile = dict_data.get("mobile")
    password = dict_data.get("password")
    # 2. 验证参数是否为空
    if not all([mobile,password]):
        return jsonify(RET.NODATA,errmsg = "参数不存在")
    # 3. 通过手机号去数据库中参看是否存在
    user = User.query.filter(User.mobile == mobile).first()
    # 4. 判断该用户是否存在
    if not user:
        return jsonify(RET.NODATA,errmsg = "用户不存在")
    # 5. 判断密码是否一致
    if password != user.password_hash:
        return jsonify(RET.DATAERR,errmsg = "密保不一致")
    # 6. 保存用户的登陆状态在session
    session["user_id"] = user.id
    session["nick_name"] = user.nick_name
    session["user_mobile"] = user.mobile
    # 7. 返回数据
    return jsonify(errno = RET.OK,errmsg="成功")
# 注册用户
@passport_blue.route('/register', methods=['POST'])
def register():
    # 1. 获取参数
    dict_data = request.json
    mobile = dict_data.get("mobile")
    sms_code = dict_data.get("sms_code")
    password = dict_data.get("password")
    # 2. 判断参数是否为空
    if not all([mobile,sms_code,password]):
        return jsonify(errno=RET.NODATA,errmsg="参数有空值")
    # 3. 手机号码格式验证
    if not re.match("1[35789]\d{9}",mobile):
        return jsonify(errno=RET.DATAERR,errmsg="手机格式不正确")
    # 4. 根据手机号,去redis中获取验证码
    try:
        redis_sms_code = redis_store.get("sms_code:%s" % mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR,errmsg="获取验证码失败")
    # 5. 判断验证码是否过期
    if not redis_sms_code:
        return jsonify(errno=RET.NODATA,errmsg = "参数已过期")
    # 5.1 删除redis验证码
    try:
        redis_store.delete("sms_code:%s" % mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR,errmsg="获取验证码失败")
    # 6. 判断获取到的验证码和redis中的是否相等
    if sms_code != redis_sms_code:
        return jsonify(errno=RET.PWDERR,errmsg = "验证码不相同")
    # 7. 创建User对象,设置属性
    user = User()
    user.nick_name = mobile
    user.password_hash = password
    user.mobile = mobile

    # 8. 保存用户到数据库
    db.session.add(user)
    db.session.commit()
    # 9. 放回状态
    return jsonify(errno=RET.OK,errmsg="成功")
# 获取短信验证码
@passport_blue.route('/sms_code', methods=['POST'])
def sms_code():
    # 1. 获取参数
    # dict_data = request.json
    json_data = request.data
    dict_data = json.loads(json_data)
    mobile = dict_data.get("mobile")
    image_code = dict_data.get("image_code")
    image_code_id = dict_data.get("image_code_id")
    # 2. 判断参数是否为空
    if not all([mobile,image_code,image_code_id]):
        return jsonify(errno=RET.PARAMERR,errmsg="参数验证不全")
    # 3. 验证手机号参数
    if not re.match("1[35789]\d{9}",mobile):
        return jsonify(errno=RET.DATAERR,errmsg="手机号码格式错误")
    # 4. 通过验证码编号，取出图片验证码
    try:
        redis_image_code = redis_store.get("image_code:%s" % image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR,errmsg="获取验证码失败")
    # 5. 判断验证码是否过期
    if not redis_image_code:
        return jsonify(erron=RET.NODATA,errmsg="验证码不存在")
    # 6. 删除redis中的验证码
    try:
        redis_store.delete("image_code:%s" % image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PWDERR,errmsg="获取验证码异常")


    # 7. 判断验证码和redis中的是否相等
    if redis_image_code.lower() != image_code.lower():
        return jsonify(errno=RET.DATAERR,errmsg="图片验证码不相等")
    # 8. 生成验证码
    sms_code = "%06d" % random.randint(0,999999)
    # 9. 通过ccp发送验证码
    ccp = CCP()
    try:
        result = ccp.send_template_sms(mobile,[sms_code, constants.IMAGE_CODE_REDIS_EXPIRES/60], 1)

    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg="云通讯发送异常")
    if result == -1:
        return jsonify(errno=RET.DATAERR, errmsg="短信发送失败")
    # 10. 存储验证码到redis中
    try:
        redis_store.set("sms_code:%s"% mobile,sms_code,constants.IMAGE_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="保存图片验证码失败")
    # 11. 返回发送状态
    return jsonify(errno=RET.OK,errmsg = "返回成功")
# 获取图片验证码
@passport_blue.route('/image_code')
def image_code():
    # 1. 接受参数
    cur_id = request.args.get("cur_id")
    pre_id = request.args.get("pre_id")
    # 2. 验证参数
    if not cur_id:
        return jsonify(errno=RET.PARAMERR, errmsg="参数不正确")
    # 3. 生成图片验证码
    name, text, image_data = captcha.generate_captcha()
    # 4. 记录到redis中
    try:
        redis_store.set("image_code:%s" % cur_id,text,constants.IMAGE_CODE_REDIS_EXPIRES)
        # 5. 判断上一个编号是否存在,有则删除
        if pre_id:
            redis_store.delete("image_code:%s" % pre_id)
    except Exception as e:
        return  jsonify(errno=RET.DBERR,errmsg = "图片操作异常")

    # 6. 返回图片
    response = make_response(image_data)
    response.headers["Content-Type"] = "image/jpg"
    return response
    # return image_data
