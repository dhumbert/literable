import Image
import os
import re
from flask import send_from_directory
from pyread import book_upload_set, cover_upload_set, db


def get_books():
    return Book.query.order_by(Book.title).all()


def get_book(id):
    return Book.query.get_or_404(id)


def get_books_by_tag(slug):
    tag = Tag.query.filter_by(slug=slug).first_or_404()
    books = db.session.query(Book).with_parent(tag, 'books').order_by(Book.title)
    books = None if books.count() == 0 else books

    return (books, tag)


def get_books_by_genre(slug):
    genre = Genre.query.filter_by(slug=slug).first_or_404()
    books = db.session.query(Book).with_parent(genre, 'books').order_by(Book.title)
    books = None if books.count() == 0 else books

    return (books, genre)


def add_book(form, files):
        filename = book_upload_set.save(files['file'])
        cover = cover_upload_set.save(files['cover'])

        create_thumbnail(cover)

        book = Book()
        book.title = form['title']
        book.author = form['author']
        book.filename = filename
        book.cover = cover
        book.genre_id = form['genre'] if form['genre'] else None
        book.update_tags(form['tags'])

        db.session.add(book)
        db.session.commit()

        return True


def edit_book(id, form, files):
    book = get_book(id)
    if book:
        book.title = form['title']
        book.author = form['author']
        book.genre_id = form['genre'] if form['genre'] else None
        book.attempt_to_update_file(files['file'])
        book.attempt_to_update_cover(files['cover'])
        book.update_tags(form['tags'])
        db.session.commit()
        return True
    return False


def download_book(id):
    book = get_book(id)
    if book:
        return send_from_directory(book_upload_set.config.destination, book.filename)


def create_thumbnail(file):
    image = Image.open(cover_upload_set.path(file))
    image.thumbnail((70, 100), Image.ANTIALIAS)
    new_filename = "thumb-%s" % file
    image.save(cover_upload_set.path(new_filename))

_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')


def slugify(text, delim=u'-'):
    """Generates an ASCII-only slug."""
    result = []
    for word in _punct_re.split(text.lower()):
        if word:
            result.append(word)
    return unicode(delim.join(result))


def get_tags():
    return Tag.query.order_by(Tag.name).all()


def get_genres():
    return Genre.query.order_by(Genre.name).all()


books_tags = db.Table('books_tags',
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id')),
    db.Column('book_id', db.Integer, db.ForeignKey('books.id'))
)


class Tag(db.Model):
    __tablename__ = 'tags'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    slug = db.Column(db.String)

    def generate_slug(self, depth=0):
        search_for = slugify(self.name)

        if depth > 0:
            search_for = slugify("%s-%d" % (self.name, depth))

        result = Tag.query.filter_by(slug=search_for).first()
        if result is None:
            return search_for
        else:
            return self.generate_slug(depth + 1)


class Book(db.Model):
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    author = db.Column(db.String)
    filename = db.Column(db.String)
    cover = db.Column(db.String)

    tags = db.relationship('Tag', secondary=books_tags, backref=db.backref('books', lazy='dynamic'), order_by=[Tag.name])
    genre_id = db.Column(db.Integer, db.ForeignKey('genres.id'))
    genre = db.relationship('Genre')

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

    def get_tag_string(self):
        tags = [tag.name for tag in self.tags]
        return ', '.join(tags)

    def empty_tags(self):
        self.tags[:] = []
        db.session.flush()

    def update_tags(self, tag_string):
        self.empty_tags()

        for tag in tag_string.split(','):
            name = tag.strip().lower()
            if len(name) > 0:
                # check for existing tag
                t = Tag.query.filter_by(name=name).first()
                if t is None:
                    t = Tag()
                    t.name = name
                    t.slug = t.generate_slug()

                self.tags.append(t)


class Genre(db.Model):
    __tablename__ = 'genres'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    slug = db.Column(db.String)

    books = db.relationship('Book', backref=db.backref('books'), order_by=[Book.title])

