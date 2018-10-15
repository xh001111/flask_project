from utils.captcha.captcha import captcha
from . import image_code
from flask import request
from info import redis_store
@image_code.route('/image_code')
def img_data():
    # 1. 接受参数
    cur_id = request.args.get("cur_id")
    pre_id = request.args.get("pre_id")
    # 2. 验证参数
    if not cur_id:
        return "没有接受到图片随机数"
    # 3. 生成图片验证码
    name, text, image_data = captcha.generate_captcha()
    # 4. 记录到redis中
    redis_store.set("image_code%s" % cur_id,text,100)
    # 5. 判断上一个编号是否存在,有则删除
    if pre_id :
        redis_store.delete("image_code%s" % pre_id)
    # 6. 返回图片
    return image_data