import os
from functools import wraps
from flask import Flask, make_response
from flaskext import uploads
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from seshat.filters import nl2br, none2blank


app = Flask(__name__, instance_relative_config=True)
app.config.from_object('seshat.config')
app.config.from_pyfile('application.cfg')

db = SQLAlchemy(app)

login = LoginManager()
login.init_app(app)
login.login_view = "login"

app.jinja_env.filters['nl2br'] = nl2br
app.jinja_env.filters['none2blank'] = none2blank
app.jinja_env.globals['len'] = len
app.jinja_env.globals['demo'] = app.config['DEMO']

#uploads
current_path = os.path.dirname(os.path.abspath(__file__))
app.config['UPLOADS_DEFAULT_DEST'] = os.path.join(current_path, os.path.join('static', 'uploads'))
app.config['UPLOADS_DEFAULT_URL'] = '/static/uploads/'

book_upload_set = uploads.UploadSet('books', extensions=app.config['EBOOK_EXTENSIONS'], default_dest=lambda x: app.config['LIBRARY_PATH'])
cover_upload_set = uploads.UploadSet('covers', uploads.IMAGES)

uploads.configure_uploads(app, (book_upload_set, cover_upload_set))


def content_type(content_type):
    """Adds Content-type header to requests"""
    def decorator(func):
        @wraps(func)
        def do_output(*args, **kwargs):
            response = make_response(func(*args, **kwargs))
            response.headers['Content-type'] = content_type
            return response
        return do_output
    return decorator

@login.user_loader
def load_user(id):
    from seshat.orm import User
    return User.query.get(int(id))

import seshat.views
