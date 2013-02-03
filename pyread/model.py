import Image
import os
from flask import send_from_directory
from pyread import book_upload_set, cover_upload_set, db


def get_books():
    return Book.query.order_by(Book.title).all()


def get_book(id):
    return Book.query.get(id)


def save_book(attrs):
        filename = book_upload_set.save(attrs[2])
        cover = cover_upload_set.save(attrs[3])

        create_thumbnail(cover)

        book = Book()
        book.title = attrs[0]
        book.author = attrs[1]
        book.filename = filename
        book.cover = cover

        db.session.add(book)
        db.session.commit()

        return True


def edit_book(id, form, files):
    book = get_book(id)
    if book:
        book.title = form['title']
        book.author = form['author']
        book.attempt_to_update_file(files['file'])
        book.attempt_to_update_cover(files['cover'])
        db.session.commit()


def download_book(id):
    book = get_book(id)
    if book:
        return send_from_directory(book_upload_set.config.destination, book.filename)


def create_thumbnail(file):
    image = Image.open(cover_upload_set.path(file))
    image.thumbnail((70, 100), Image.ANTIALIAS)
    new_filename = "thumb-%s" % file
    image.save(cover_upload_set.path(new_filename))


class Book(db.Model):
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    author = db.Column(db.String)
    filename = db.Column(db.String)
    cover = db.Column(db.String)

    def get_thumb_url(self):
        return cover_upload_set.url('thumb-' + self.cover)

    def get_format(self):
        if self.filename:
            return os.path.splitext(self.filename)[1][1:]
        else:
            return None

    def attempt_to_update_file(self, file):
        try:
            filename = book_upload_set.save(file)
            if self.filename:
                # remove current file if user uploaded new one
                try:
                    os.remove(book_upload_set.path(self.filename))
                except:
                    pass  # can't delete old book. not the end of the world.

            self.filename = filename
        except:
            pass  # couldn't upload book. maybe blank upload?

    def attempt_to_update_cover(self, file):
        try:
            cover = cover_upload_set.save(file)
            if self.cover:
                # remove current cover if user uploaded new one
                try:
                    os.remove(cover_upload_set.path(self.cover))
                except:
                    pass  # can't delete old cover. not the end of the world.

            self.cover = cover
            create_thumbnail(cover)
        except:
            pass  # couldn't upload cover. maybe blank upload?
