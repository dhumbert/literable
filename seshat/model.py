from datetime import datetime
import hashlib
from flask import url_for, flash
from seshat import db, app
from seshat.orm import Book, Genre, Tag, Series, Author, User


def _get_page(page):
    if page is None:
        page = 1
    else:
        page = int(page)
    return page


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
    return Book.query.order_by('created_at desc, id desc').paginate(page, per_page=app.config['BOOKS_PER_PAGE'])


def get_books_by_tag(slug, page):
    page = max(1, _get_page(page))

    tag = Tag.query.filter_by(slug=slug).first_or_404()
    books = Book.query.filter(Book.tags.any(Tag.id == tag.id)).order_by(Book.title).paginate(page, per_page=app.config['BOOKS_PER_PAGE'])
    books = None if len(books.items) == 0 else books

    return (books, tag)


def get_books_by_genre(slug, page):
    page = max(1, _get_page(page))

    genre = Genre.query.filter_by(slug=slug).first_or_404()
    books = Book.query.filter_by(genre_id=genre.id).order_by(Book.title).paginate(page, per_page=app.config['BOOKS_PER_PAGE'])
    books = None if len(books.items) == 0 else books

    return (books, genre)


def get_books_by_series(slug, page):
    page = max(1, _get_page(page))

    sery = Series.query.filter_by(slug=slug).first_or_404()
    books = Book.query.filter_by(series_id=sery.id).order_by(Book.series_seq).paginate(page, per_page=app.config['BOOKS_PER_PAGE'])
    books = None if len(books.items) == 0 else books

    return (books, sery)


def get_books_by_author(slug, page):
    page = max(1, _get_page(page))

    author = Author.query.filter_by(slug=slug).first_or_404()
    books = Book.query.filter_by(author_id=author.id).order_by(Book.title).paginate(page, per_page=app.config['BOOKS_PER_PAGE'])
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

    if 'tags' in form:
        book.update_tags(form['tags'])

    book.update_series(form['series'], form['series_seq'])
    #book.created_at = datetime.now()

    if 'file' in files:
        book.attempt_to_update_file(files['file'])

    if 'cover' in files:
        book.attempt_to_update_cover(files['cover'])

    db.session.add(book)
    db.session.commit()

    if app.config['WRITE_META_ON_SAVE']:
        book.write_meta()

    return True


def edit_book(id, form, files):
    book = get_book(id)
    if book:
        # user is adding a new genre
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

        if 'tags' in form:
            book.update_tags(form['tags'])
        else:
            book.empty_tags()

        db.session.commit()

        if app.config['WRITE_META_ON_SAVE']:
            book.write_meta()

        return True
    return False


def delete_book(id):
    book = get_book(id)

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


def add_user(username, password):
    u = User()
    u.username = username
    u.set_password(password)
    db.session.add(u)
    db.session.commit()
    return u.id


def get_users():
    return User.query.order_by(User.username).all()


def delete_user(username):
    u = User.query.filter_by(username=username).first()
    db.session.delete(u)
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
    output = """<a href="%s">%s</a>""" % (url_for('genre', genre=parent.slug), output + parent.name)

    if parent.children:
        output = output + "<ul>"
        for child in parent.children:
            output = output + _recurse_list_level(child)

        output = output + "</ul>"

    output = output + "</li>"
    return output


def authenticate(username, password):
    hashed_pass = hashlib.sha1(password).hexdigest()
    users = db.session.query(User).filter(User.username==username)
    for user in users:
        return user

    return None