import os
from pyread import db, book_upload_set, cover_upload_set, utils


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
