from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from api.extensions import db
from api.autoapp import app


migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command("db", MigrateCommand)


if __name__ == "__main__":
    manager.run()
