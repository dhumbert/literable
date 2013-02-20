from flask.ext.script import Manager
from flask.ext.alembic import ManageMigrations
from seshat import app, model


manager = Manager(app)
manager.add_command("migrate", ManageMigrations())


@manager.command
def debug():
    """ Run the server in debug mode"""
    app.run('0.0.0.0', debug=True)


@manager.command
def write_meta():
    for book in model.get_all_books():
        print "Writing meta for %s" % book.title
        book.write_meta()


if __name__ == "__main__":
    manager.run()
