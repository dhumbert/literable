import os
import os.path
import hashlib
import shutil
from flask import url_for
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.ext.associationproxy import association_proxy
from literable import db, book_upload_set, book_staging_upload_set, cover_upload_set, utils, epub, app


books_taxonomies = db.Table('books_taxonomies',
    db.Column('taxonomy_id', db.Integer, db.ForeignKey('taxonomies.id')),
    db.Column('book_id', db.Integer, db.ForeignKey('books.id'))
)


class Taxonomy(db.Model):
    __tablename__ = 'taxonomies'
    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('taxonomies.id'))
    parent = db.relationship('Taxonomy', backref=db.backref('children'), remote_side=[id])
    name = db.Column(db.String)
    type = db.Column(db.String)
    slug = db.Column(db.String)

    def get_parents(self):
        parents = []
        if self.parent_id:
            parent = Taxonomy.query.get(self.parent_id)
            if parent:
                parents.append(parent)
                parents = parent.get_parents() + parents

        return parents

    def generate_slug(self, depth=0):
        search_for = utils.slugify(self.name)

        if depth > 0:
            search_for = utils.slugify("%s-%d" % (self.name, depth))

        result = Taxonomy.query.filter_by(slug=search_for).first()
        if result is None:
            return search_for
        else:
            return self.generate_slug(depth + 1)

    @classmethod
    def get_grouped_counts(cls, ttype, order):
        q = db.session.query(Taxonomy.name, Taxonomy.slug, Taxonomy.id, Taxonomy.type,
                         db.func.count(books_taxonomies.c.book_id).label('count_books'))\
        .filter_by(type=ttype)\
        .outerjoin(books_taxonomies).group_by(Taxonomy.name, Taxonomy.slug, Taxonomy.id, Taxonomy.type)

        if not order or order == 'name':
            q = q.order_by(Taxonomy.name.asc())
        elif order == 'count':
            q = q.order_by(db.desc('count_books'))

        return q.all()

    def __repr__(self):
        return self.name


class Book(db.Model):
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    filename = db.Column(db.String)
    cover = db.Column(db.String)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime())
    rating = db.Column(db.Integer())
    public = db.Column(db.Boolean())
    series_seq = db.Column(db.Integer)

    taxonomies = db.relationship('Taxonomy', secondary=books_taxonomies, backref=db.backref('books'))

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', backref=db.backref('books'))

    @property
    def authors(self):
        return self._get_tax_by_type('author')

    @property
    def publishers(self):
        return self._get_tax_by_type('publisher')

    @property
    def genres(self):
        return self._get_tax_by_type('genre')

    @property
    def tags(self):
        return self._get_tax_by_type('tag')

    @property
    def series(self):
        return self._get_tax_by_type('series')

    def _get_tax_by_type(self, type):
        return filter(lambda t: t.type == type, self.taxonomies)

    def get_cover_url(self):
        if self.cover:
            return cover_upload_set.url(self.cover)
        else:
            return url_for('static', filename='img/default.jpg')

    def get_format(self):
        if self.filename:
            return os.path.splitext(self.filename)[1][1:]
        else:
            return None

    def remove_file(self):
        if self.filename:
            os.remove(book_upload_set.path(self.filename))
            self.filename = None

    def remove_cover(self):
        if self.cover:
            os.remove(cover_upload_set.path(self.cover))
            self.cover = None

    def move_file_from_staging(self, filename):
        if self.filename:
            self.remove_file()

        if filename:
            self.filename = filename
            src = book_staging_upload_set.path(self.filename)
            dest_path = app.config['LIBRARY_PATH']

            if os.path.exists(os.path.join(dest_path, self.filename)):
                self.filename = book_upload_set.resolve_conflict(dest_path, self.filename)

            shutil.move(src, book_upload_set.path(self.filename))


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
        except:
            pass  # couldn't upload cover. maybe blank upload?

    def get_tag_string(self):
        tags = [tag.name for tag in self.tags]
        return ', '.join(tags)

    def update_taxonomies(self, tax_map):
        self.taxonomies = []
        for tax_slug, terms in tax_map.iteritems():
            for term_name in terms:
                if term_name.strip():
                    tax = Taxonomy.query.filter_by(type=tax_slug, name=term_name.strip()).first()
                    if not tax:
                        tax = Taxonomy()
                        tax.type = tax_slug
                        tax.name = term_name.strip()
                        tax.slug = tax.generate_slug()
                        db.session.add(tax)

                    if tax not in self.taxonomies:
                        self.taxonomies.append(tax)

    def write_meta(self):
        if self.filename:
            if self.get_format() == 'epub':
                self._write_epub_meta()

    def _write_epub_meta(self):
        epub_file = book_upload_set.path(self.filename)

        title = self._build_meta_title()

        if self.cover:
            cover = cover_upload_set.path(self.cover)
        else:
            cover = None

        if self.genres:
            genre = [genre.name for genre in self.genres]
        else:
            genre = []

        if self.tags:
            tags = [tag.name for tag in self.tags]
        else:
            tags = []

        if self.authors:
            author = self.authors[0].name
        else:
            author = None

        subjects = genre + tags

        epub.write_epub_meta(epub_file, title, author,
            description=self.description,
            cover=cover,
            subjects=subjects)

    def _build_meta_title(self):
        title = self.title
        if app.config['ADD_SERIES_TO_META_TITLE']:
            if self.series:
                prepend_title = self.series[0].name
                if self.series_seq:
                    prepend_title = "%s %d - " % (prepend_title, self.series_seq)

                title = prepend_title + title
        return title

    def rate(self, score):
        self.rating = score
        db.session.commit()


class ReadingList(db.Model):
    __tablename__ = 'reading_list'
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    position = db.Column(db.Integer)

    book = db.relationship(Book)


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    password = db.Column(db.String)
    admin = db.Column(db.Boolean)

    _reading_list = db.relationship(ReadingList, order_by=[ReadingList.position],
                                    collection_class=ordering_list('position'))
    reading_list = association_proxy('_reading_list', 'book')

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def set_password(self, password):
        self.password = hashlib.sha1(password).hexdigest()

    def __repr__(self):
        return unicode(self.username)

