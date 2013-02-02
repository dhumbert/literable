from flask import Flask
from flaskext import uploads
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['LIBRARY_PATH'] = "/Users/dhumbert/tmp/books/"

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://goread:goread@localhost:5432/goread'
db = SQLAlchemy(app)
#db.create_all()

book_upload_set = uploads.UploadSet('books', extensions=('txt', 'rtf', 'epub', 'mobi', 'pdf'), default_dest=lambda x: app.config['LIBRARY_PATH'])

uploads.configure_uploads(app, (book_upload_set))

import pyread.views
