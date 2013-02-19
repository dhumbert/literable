from flask.ext.script import Manager
from flask.ext.alembic import ManageMigrations
from seshat import app, epub


manager = Manager(app)
manager.add_command("migrate", ManageMigrations())


@manager.command
def debug():
    """ Run the server in debug mode"""
    app.run('0.0.0.0', debug=True)


@manager.command
def write_epub_metadata():
    epub.write_all_meta()


if __name__ == "__main__":
    manager.run()
