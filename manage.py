#!/usr/bin/env python
from flask.ext.script import Manager
from flask.ext.alembic import ManageMigrations
from literable import app, model


manager = Manager(app)
manager.add_command("migrate", ManageMigrations())


@manager.command
def debug():
    """ Run the server in debug mode"""
    app.run('0.0.0.0', debug=True)


@manager.command
def write_meta():
    """Write meta to ebook files"""
    for book in model.get_all_books():
        print "Writing meta for %s" % book.title
        book.write_meta()


@manager.command
def add_user(username, password):
    id = model.add_user(username, password)
    print "User added with ID {0}".format(id)


@manager.command
def list_users():
    for user in model.get_users():
        print user


@manager.command
def delete_user(username):
    model.delete_user(username)
    print "User deleted"

if __name__ == "__main__":
    manager.run()
