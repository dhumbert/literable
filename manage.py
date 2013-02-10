from flask.ext.script import Manager
from flask.ext.alembic import ManageMigrations
from seshat import app


manager = Manager(app)
manager.add_command("migrate", ManageMigrations())


@manager.command
def debug():
    """ Run the server in debug mode"""
    app.run('0.0.0.0', debug=True)


if __name__ == "__main__":
    manager.run()
