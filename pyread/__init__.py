import os
from functools import wraps
from flask import Flask, make_response
from flaskext import uploads
from flask.ext.sqlalchemy import SQLAlchemy
from pyread.filters import nl2br, none2blank


app = Flask(__name__, instance_relative_config=True)
app.config.from_object('pyread.config')
app.config.from_pyfile('application.cfg')

db = SQLAlchemy(app)
#db.create_all()

app.jinja_env.filters['nl2br'] = nl2br
app.jinja_env.filters['none2blank'] = none2blank

#uploads
current_path = os.path.dirname(os.path.abspath(__file__))
app.config['UPLOADS_DEFAULT_DEST'] = os.path.join(current_path, os.path.join('static', 'uploads'))
app.config['UPLOADS_DEFAULT_URL'] = '/static/uploads/'

book_upload_set = uploads.UploadSet('books', extensions=('txt', 'rtf', 'epub', 'mobi', 'pdf'), default_dest=lambda x: app.config['LIBRARY_PATH'])
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

import pyread.views
