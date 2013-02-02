import Image
from flask import send_from_directory
from pyread import book_upload_set, cover_upload_set, db


def get_books():
    return Book.query.order_by(Book.title).all()


def save_book(attrs):
        filename = book_upload_set.save(attrs[2])
        cover = cover_upload_set.save(attrs[3])

        create_thumbnail(cover)

        book = Book(attrs[0], attrs[1], filename, cover)
        db.session.add(book)
        db.session.commit()

        return True


def download_book(id):
    book = Book.query.get(id)
    if book:
        return send_from_directory(book_upload_set.config.destination, book.filename, as_attachment=True)


def create_thumbnail(file):
    image = Image.open(cover_upload_set.path(file))
    image.thumbnail((75, 100), Image.ANTIALIAS)
    new_filename = "thumb-%s" % file
    image.save(cover_upload_set.path(new_filename))


class Book(db.Model):
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    author = db.Column(db.String)
    filename = db.Column(db.String)
    cover = db.Column(db.String)

    def __init__(self, title, author, filename, cover):
        self.title = title
        self.author = author
        self.filename = filename
        self.cover = cover

    def get_thumb_url(self):
        return cover_upload_set.url('thumb-' + self.cover)
