import os
from functools import wraps
from flask import Flask, make_response
from flaskext import uploads
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['LIBRARY_PATH'] = "/Users/dhumbert/tmp/books/"
app.secret_key = "=JbX0gvs3ivIZkST+HI"

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://goread:goread@localhost:5432/goread'
db = SQLAlchemy(app)
#db.create_all()

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
