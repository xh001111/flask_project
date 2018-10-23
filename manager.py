import random
from datetime import datetime, timedelta

from flask import current_app

from info import create_app, db
from flask_script import Manager
from info import models
from flask_migrate import Migrate,MigrateCommand

from info.models import User

app = create_app("develop")

manager = Manager(app)

Migrate(app,db)

manager.add_command("db",MigrateCommand)

@manager.option('-u', '--username', dest='username')
@manager.option('-p', '--password', dest='password')
def create_supername(username,password):
    admin = User()

    admin.nick_name = username
    admin.password = password
    admin.mobile = username
    admin.is_admin = True

    try:
        db.session.add(admin)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return "创建失败"

    return "创建成功"
@manager.option('-t', '--test', dest='test')
def test_man(test):
    user_list = []
    for i in range(0,10000):
        user = User()
        user.nick_name = "HuiZong%d" % i
        user.password_hash = "pbkdf2:sha256:50000$GoZLwJaV$e394b564f61746f70b96d61f4fc15d6532bd896c173ec1f41c0e4e7f8e7bd95f"
        user.mobile = "155%08d" % i
        user.last_login = datetime.now() - timedelta(seconds=random.randint(0, 3600 * 24 * 31))
        user.is_admin = False
        user_list.append(user)

    try:
        db.session.add_all(user_list)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return "创建失败"

    return "创建成功"


if __name__ == "__main__":

    manager.run()