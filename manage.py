from flask.ext.script import Manager
from flask.ext.alembic import ManageMigrations
from seshat import app


manager = Manager(app)
manager.add_command("migrate", ManageMigrations())


if __name__ == "__main__":
    manager.run()
