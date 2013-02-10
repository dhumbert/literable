from flask.ext.script import Manager
from flask.ext.alembic import ManageMigrations
from seshat import app


manager = Manager(app)
manager.add_command("migrate", ManageMigrations())


@manager.command
def run():
    """Run Seshat using the built-in server"""
    app.run(debug=True, host='0.0.0.0')


if __name__ == "__main__":
    manager.run()
