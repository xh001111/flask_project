from flask import session

from info import create_app
from flask_script import Manager
from flask_migrate import Migrate,MigrateCommand

app = create_app("develop")

manager = Manager(app)
Migrate(db,app)

app.add
@app.route("/")
def hello_world():

    session["name"] = "zhangsan"
    print(session.get("name"))

    return "helloworld"


if __name__ == "__main__":

    app.run()