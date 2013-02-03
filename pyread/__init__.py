import os
from flask import Flask
from flaskext import uploads
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['LIBRARY_PATH'] = "/Users/dhumbert/tmp/books/"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
db = SQLAlchemy(app)
#db.create_all()

#uploads
current_path = os.path.dirname(os.path.abspath(__file__))
app.config['UPLOADS_DEFAULT_DEST'] = os.path.join(current_path, os.path.join('static', 'uploads'))
app.config['UPLOADS_DEFAULT_URL'] = '/static/uploads/'

book_upload_set = uploads.UploadSet('books', extensions=('txt', 'rtf', 'epub', 'mobi', 'pdf'), default_dest=lambda x: app.config['LIBRARY_PATH'])
cover_upload_set = uploads.UploadSet('covers', uploads.IMAGES)

uploads.configure_uploads(app, (book_upload_set, cover_upload_set))

import pyread.views
