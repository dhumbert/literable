import os
from flask import url_for
from seshat import db, book_upload_set, cover_upload_set, utils, epub


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
        search_for = utils.slugify(self.name)

        if depth > 0:
            search_for = utils.slugify("%s-%d" % (self.name, depth))

        result = Tag.query.filter_by(slug=search_for).first()
        if result is None:
            return search_for
        else:
            return self.generate_slug(depth + 1)


class Series(db.Model):
    __tablename__ = 'series'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    slug = db.Column(db.String)
    description = db.Column(db.Text)

    def generate_slug(self, depth=0):
        search_for = utils.slugify(self.title)

        if depth > 0:
            search_for = utils.slugify("%s-%d" % (self.title, depth))

        result = Series.query.filter_by(slug=search_for).first()
        if result is None:
            return search_for
        else:
            return self.generate_slug(depth + 1)


class Author(db.Model):
    __tablename__ = 'authors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    slug = db.Column(db.String)

    def generate_slug(self, depth=0):
        search_for = utils.slugify(self.name)

        if depth > 0:
            search_for = utils.slugify("%s-%d" % (self.name, depth))

        result = Author.query.filter_by(slug=search_for).first()
        if result is None:
            return search_for
        else:
            return self.generate_slug(depth + 1)


class Book(db.Model):
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    filename = db.Column(db.String)
    cover = db.Column(db.String)
    description = db.Column(db.Text)

    tags = db.relationship('Tag', secondary=books_tags, backref=db.backref('books'), order_by=[Tag.name])
    genre_id = db.Column(db.Integer, db.ForeignKey('genres.id'))
    genre = db.relationship('Genre')

    series_id = db.Column(db.Integer, db.ForeignKey('series.id'))
    series = db.relationship('Series', backref=db.backref('books', lazy='dynamic'))
    series_seq = db.Column(db.Integer)

    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'))
    author = db.relationship('Author', backref=db.backref('books', lazy='dynamic'))

    def get_thumb_url(self):
        if self.cover:
            return cover_upload_set.url('thumb-' + self.cover)
        else:
            return url_for('static', filename='img/default.png')

    def get_format(self):
        if self.filename:
            return os.path.splitext(self.filename)[1][1:]
        else:
            return None

    def remove_file(self):
        if self.filename:
            os.remove(book_upload_set.path(self.filename))

    def remove_cover(self):
        if self.cover:
            os.remove(cover_upload_set.path(self.cover))

    def attempt_to_update_file(self, file):
        try:
            filename = book_upload_set.save(file)
            if filename:
                if self.filename:
                    # remove current file if user uploaded new one
                    try:
                        self.remove_file()
                    except:
                        pass  # can't delete old book. not the end of the world.

                self.filename = filename
        except:
            pass  # couldn't upload book. maybe blank upload?

    def attempt_to_update_cover(self, file):
        try:
            cover = cover_upload_set.save(file)
            if cover:
                if self.cover:
                    # remove current cover if user uploaded new one
                    try:
                        self.remove_cover()
                    except:
                        pass  # can't delete old cover. not the end of the world.

                self.cover = cover
                utils.create_thumbnail(cover)
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

    def update_series(self, series, seq):
        if series:
            books_series = Series.query.filter_by(title=series).first()
            if not books_series:
                books_series = Series()
                books_series.title = series
                books_series.slug = books_series.generate_slug()
                db.session.add(books_series)
            self.series = books_series

        if seq:
            self.series_seq = seq

    def update_author(self, name):
        if name:
            book_author = Author.query.filter_by(name=name).first()
            if not book_author:
                book_author = Author()
                book_author.name = name
                book_author.slug = book_author.generate_slug()
                db.session.add(book_author)
            self.author = book_author

    def write_meta(self):
        if self.filename:
            if self.get_format() == 'epub':
                self._write_epub_meta()

    def _write_epub_meta(self):
        epub_file = book_upload_set.path(self.filename)

        if self.cover:
            cover = cover_upload_set.path(self.cover)
        else:
            cover = None

        if self.series:
            series = self.series.title
        else:
            series = None

        if self.genre:
            genre = [self.genre.name]
        else:
            genre = []

        if self.tags:
            tags = [tag.name for tag in self.tags]
        else:
            tags = []

        subjects = genre + tags

        epub.write_epub_meta(epub_file, self.title, self.author.name,
            description=self.description,
            cover=cover, series=series,
            series_seq=self.series_seq,
            subjects=subjects)


class Genre(db.Model):
    __tablename__ = 'genres'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    slug = db.Column(db.String)
    parent_id = db.Column(db.Integer, db.ForeignKey('genres.id'))

    children = db.relationship("Genre", backref=db.backref("genres", remote_side=id))

    books = db.relationship('Book', backref=db.backref('books'), order_by=[Book.title])

    def get_parents(self):
        parents = []
        if self.parent_id:
            parent = Genre.query.get(self.parent_id)
            if parent:
                parents.append(parent)
                parents = parent.get_parents() + parents

        return parents

    def generate_slug(self, depth=0):
        search_for = utils.slugify(self.name)

        if depth > 0:
            search_for = utils.slugify("%s-%d" % (self.name, depth))

        result = Genre.query.filter_by(slug=search_for).first()
        if result is None:
            return search_for
        else:
            return self.generate_slug(depth + 1)
