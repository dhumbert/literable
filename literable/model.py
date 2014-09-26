from datetime import datetime
import hashlib
from flask import url_for, flash
from flask.ext.login import current_user
from sqlalchemy import or_, and_
from sqlalchemy.exc import IntegrityError
from elasticsearch import Elasticsearch
from literable import db, app
from literable.orm import Book, Genre, Tag, Series, Author, User, ReadingList


def _get_page(page):
    if page is None:
        page = 1
    else:
        page = int(page)
    return page


def _privilege_filter():
    return or_(current_user.admin, Book.user_id == current_user.id, Book.public)


def user_can_modify_book(book, user):
    return user.admin or book.user_id == current_user.id


def user_can_download_book(book, user):
    return book.public or user_can_modify_book(book, user)


def get_books(page):
    page = max(1, _get_page(page))
    return Book.query.order_by(Book.title).paginate(page, per_page=app.config['BOOKS_PER_PAGE'])


def get_all_books():
    return Book.query.order_by(Book.title).all()


def get_book(id):
    if id is None:
        return Book()  # blank book object
    else:
        return Book.query.get_or_404(id)


def get_recent_books(page):
    page = max(1, _get_page(page))
    return Book.query.filter(_privilege_filter()).order_by('created_at desc, id desc').paginate(page, per_page=app.config['BOOKS_PER_PAGE'])


def search_books(q, page):
    page = max(1, _get_page(page))
    return Book.query.filter(and_(Book.title.ilike("%"+q+"%"), _privilege_filter())).order_by('created_at desc, id desc').paginate(page, per_page=app.config['BOOKS_PER_PAGE'])


def get_books_by_tag(slug, page):
    page = max(1, _get_page(page))

    tag = Tag.query.filter_by(slug=slug).first_or_404()
    books = Book.query.filter(and_(Book.tags.any(Tag.id == tag.id), _privilege_filter())).order_by(Book.title).paginate(page, per_page=app.config['BOOKS_PER_PAGE'])
    books = None if len(books.items) == 0 else books

    return (books, tag)


def get_books_by_genre(slug, page):
    page = max(1, _get_page(page))

    genre = Genre.query.filter_by(slug=slug).first_or_404()

    g_ids = [genre.id] + [x.id for x in genre.children]

    books = Book.query.filter(and_(Book.genre_id.in_(g_ids), _privilege_filter())).order_by(Book.title).paginate(page, per_page=app.config['BOOKS_PER_PAGE'])
    books = None if len(books.items) == 0 else books

    return (books, genre)


def get_books_by_series(slug, page):
    page = max(1, _get_page(page))

    sery = Series.query.filter_by(slug=slug).first_or_404()
    books = Book.query.filter(and_(Book.series_id==sery.id, _privilege_filter())).order_by(Book.series_seq).paginate(page, per_page=app.config['BOOKS_PER_PAGE'])
    books = None if len(books.items) == 0 else books

    return (books, sery)


def get_books_by_author(slug, page):
    page = max(1, _get_page(page))

    author = Author.query.filter_by(slug=slug).first_or_404()
    books = Book.query.filter(and_(Book.author_id==author.id, _privilege_filter())).order_by(Book.title).paginate(page, per_page=app.config['BOOKS_PER_PAGE'])
    books = None if len(books.items) == 0 else books

    return (books, author)


def add_book(form, files):
    if 'title' not in form or not form['title'].strip():
        raise ValueError("Title must not be blank")

    # user is adding a new genre
    if 'new-genre-name' in form and form['new-genre-name'].strip() != '':
        genre_id = add_genre(form['new-genre-name'], form['new-genre-parent'])
    elif 'genre' in form:
        genre_id = form['genre']
    else:
        genre_id = None

    book = Book()
    book.title = form['title']
    book.description = form['description']
    book.genre_id = genre_id
    book.update_author(form['author'])
    book.public = True if form['privacy'] == 'public' else False
    book.user = current_user

    if 'tags' in form:
        book.update_tags(form['tags'])

    book.update_series(form['series'], form['series_seq'])
    book.created_at = datetime.now()

    if 'file' in files:
        book.attempt_to_update_file(files['file'])

    if 'cover' in files:
        book.attempt_to_update_cover(files['cover'])

    db.session.add(book)
    db.session.commit()

    if app.config['WRITE_META_ON_SAVE']:
        book.write_meta()

    book_to_elasticsearch(book)

    return True


def book_to_elasticsearch(book):
    es_doc = {'title': book.title,
              'description': book.description,
              }
    if book.series:
        es_doc['series'] = book.series.title

    if book.author:
        es_doc['author'] = book.author.name

    es = Elasticsearch(app.config['ELASTICSEARCH_NODES'])
    es.index(app.config['ELASTICSEARCH_INDEX'],
             app.config['ELASTICSEARCH_DOC_TYPE'],
             body=es_doc,
             id=book.id)


def delete_from_elasticsearch(book):
    es = Elasticsearch(app.config['ELASTICSEARCH_NODES'])
    es.delete(app.config['ELASTICSEARCH_INDEX'],
             app.config['ELASTICSEARCH_DOC_TYPE'],
             id=book.id)


def edit_book(id, form, files):
    book = get_book(id)
    if book:
        if not user_can_modify_book(book, current_user):
            return False

        old_genre_id = book.genre_id
        old_author_id = book.author_id
        old_series_id = book.series_id

        # user is adding a new genre
        if form['new-genre-name'] or form['genre']:
            if form['new-genre-name']:
                genre_id = add_genre(form['new-genre-name'], form['new-genre-parent'])
            elif form['genre']:
                genre_id = form['genre']
        else:
            genre_id = None

        book.title = form['title']
        book.description = form['description']
        book.genre_id = genre_id
        book.update_author(form['author'])
        book.attempt_to_update_file(files['file'])
        book.attempt_to_update_cover(files['cover'])
        book.update_series(form['series'], form['series_seq'])
        book.public = True if form['privacy'] == 'public' else False

        if 'tags' in form:
            book.update_tags(form['tags'])
        else:
            book.empty_tags()

        db.session.commit()

        if app.config['WRITE_META_ON_SAVE']:
            book.write_meta()

        if old_genre_id:
            delete_tax_if_possible('genre', old_genre_id)
        if old_author_id:
            delete_tax_if_possible('author', old_author_id)
        if old_series_id:
            delete_tax_if_possible('series', old_series_id)

        book_to_elasticsearch(book)

        return True
    return False


def delete_book(id):
    book = get_book(id)

    if not user_can_modify_book(book, current_user):
        flash('You cannot delete a book you do not own', 'error')
        return False

    try:
        book.remove_file()
    except:
        flash('Unable to delete file', 'error')

    try:
        book.remove_cover()
    except:
        flash('Unable to delete cover', 'error')

    db.session.delete(book)
    db.session.commit()

    delete_from_elasticsearch(book)


def get_tags():
    return Tag.query.order_by(Tag.name).all()


def get_genres():
    return Genre.query.order_by(Genre.name).all()


def get_series():
    return Series.query.order_by(Series.title).all()


def get_authors():
    return Author.query.order_by(Author.name).all()


def get_toplevel_genres():
    return Genre.query.filter_by(parent_id=None).order_by(Genre.name).all()


def add_genre(name, parent=None):
    genre = Genre()
    genre.name = name
    genre.slug = genre.generate_slug()
    genre.parent_id = parent if parent else None
    db.session.add(genre)
    db.session.commit()
    return genre.id


def delete_tax_if_possible(tax, id):
    obj = {
        'genre': Genre,
        'tag': Tag,
        'series': Series,
        'author': Author
    }[tax]

    instance = obj.query.get(int(id))
    if instance:
        if len(instance.books) == 0: # no books left, so we can delete
            delete_tax(tax, [id])


def delete_tax(tax, ids):
    obj = {
        'genre': Genre,
        'tag': Tag,
        'series': Series,
        'author': Author
    }[tax]

    for id in ids:
        t = obj.query.get(int(id))
        db.session.delete(t)

    db.session.commit()


def add_user(username, password):
    u = User()
    u.username = username
    u.set_password(password)
    u.admin = False
    db.session.add(u)
    db.session.commit()
    return u.id


def get_users():
    return User.query.order_by(User.username).all()


def delete_user(username):
    u = User.query.filter_by(username=username).first()
    db.session.delete(u)
    db.session.commit()


def update_reading_list_order(user, ordering):
    print ordering
    for r in ReadingList.query.filter_by(user_id=user.id).all():
        r.position = ordering[unicode(r.book_id)]

    db.session.commit()


def add_to_reading_list(user, book_id):
    r = ReadingList()
    r.user_id = user.id
    r.book_id = book_id
    r.position = 999

    try:
        db.session.add(r)
        db.session.commit()
    except IntegrityError:
        pass


def is_book_in_reading_list(book_id):
    return ReadingList.query.filter_by(user_id=current_user.id, book_id=book_id).first()


def remove_from_reading_list(user, book_id):
    r = ReadingList.query.filter_by(user_id=user.id, book_id=book_id).first()
    db.session.delete(r)
    db.session.commit()


def generate_genre_tree_select_options(selected=None):
    output = ""

    for parent in get_toplevel_genres():
        output = output + _recurse_select_level(parent, selected=selected)

    return output


def _recurse_select_level(parent, depth=0, selected=None):
    name = ("&mdash;" * depth) + " " + parent.name

    selected_string = """ selected="selected" """ if selected == parent.id else ""

    output = """<option value="%s"%s>%s</option>""" % (parent.id, selected_string, name)

    if parent.children:
        for child in parent.children:
            output = output + _recurse_select_level(child, depth=depth + 1, selected=selected)

    return output


def generate_genre_tree_list():
    output = ""

    for parent in get_toplevel_genres():
        output = output + _recurse_list_level(parent)

    return output


def _recurse_list_level(parent):
    output = "<li>"
    output = output + """<span class="delete-checkbox" style="display:none;"><input type="checkbox" name="delete" value="%d"></span>""" % parent.id
    output = output + """<a href="%s">%s</a>""" % (url_for('genre', genre=parent.slug), parent.name)

    if parent.children:
        output = output + "<ul>"
        for child in parent.children:
            output = output + _recurse_list_level(child)

        output = output + "</ul>"

    output = output + "</li>"
    return output


def authenticate(username, password):
    hashed_pass = hashlib.sha1(password).hexdigest()
    user = db.session.query(User).filter(User.username==username).first()
    if user and user.password == hashed_pass:
        return user

    return None
