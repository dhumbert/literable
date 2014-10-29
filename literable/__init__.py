import os
import logging
from functools import wraps
from flask import Flask, make_response, abort
from flaskext import uploads
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager, current_user
from flaskext.markdown import Markdown
from literable.filters import nl2br, none2blank


app = Flask(__name__, instance_relative_config=True)
app.config.from_object('literable.config')
app.config.from_pyfile('application.cfg')

# Log only in production mode.

if not app.debug:
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.WARNING)
    app.logger.addHandler(stream_handler)

db = SQLAlchemy(app)

Markdown(app)

login = LoginManager()
login.init_app(app, add_context_processor=True)
login.login_view = "login"

app.jinja_env.filters['nl2br'] = nl2br
app.jinja_env.filters['none2blank'] = none2blank
app.jinja_env.globals['hasattr'] = hasattr
app.jinja_env.globals['len'] = len
app.jinja_env.globals['demo'] = app.config['DEMO']

#uploads
current_path = os.path.dirname(os.path.abspath(__file__))
app.config['UPLOADS_DEFAULT_DEST'] = os.path.join(current_path, os.path.join('static', 'uploads'))
app.config['UPLOADS_DEFAULT_URL'] = '/static/uploads/'

book_staging_upload_set = uploads.UploadSet('bookstaging', extensions=app.config['EBOOK_EXTENSIONS'], default_dest=lambda x: app.config['LIBRARY_STAGING_PATH'])
book_upload_set = uploads.UploadSet('books', extensions=app.config['EBOOK_EXTENSIONS'], default_dest=lambda x: app.config['LIBRARY_PATH'])
cover_upload_set = uploads.UploadSet('covers', uploads.IMAGES)
tmp_cover_upload_set = uploads.UploadSet('tmpcovers', uploads.IMAGES)

uploads.configure_uploads(app, (book_upload_set, cover_upload_set, book_staging_upload_set, tmp_cover_upload_set))


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


def admin_required(func):
    """Requires user to be an Admin for a view"""
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if current_user and current_user.admin:
            return func(*args, **kwargs)
        else:
            abort(403)
    return decorated_view

@login.user_loader
def load_user(id):
    from literable.orm import User
    return User.query.get(int(id))

import literable.views
