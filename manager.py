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


if __name__ == "__main__":

    manager.run()