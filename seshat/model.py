from flask import send_from_directory, url_for, flash
from seshat import book_upload_set, db
from seshat.orm import Book, Genre, Tag, Series


def get_books():
    return Book.query.order_by(Book.title).all()


def get_book(id):
    if id is None:
        return Book()  # blank book object
    else:
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


def get_books_by_series(slug):
    sery = Series.query.filter_by(slug=slug).first_or_404()
    books = db.session.query(Book).with_parent(sery, 'books').order_by(Book.series_seq)
    books = None if books.count() == 0 else books

    return (books, sery)


def add_book(form, files):
        # user is adding a new genre
        if form['new-genre-name']:
            genre_id = add_genre(form['new-genre-name'], form['new-genre-parent'])
        elif form['genre']:
            genre_id = form['genre']
        else:
            genre_id = None

        book = Book()
        book.title = form['title']
        book.author = form['author']
        book.description = form['description']
        book.genre_id = genre_id
        book.update_tags(form['tags'])
        book.update_series(form['series'], form['series_seq'])

        book.attempt_to_update_file(files['file'])
        book.attempt_to_update_cover(files['cover'])

        db.session.add(book)
        db.session.commit()

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
        book.author = form['author']
        book.description = form['description']
        book.genre_id = genre_id
        book.attempt_to_update_file(files['file'])
        book.attempt_to_update_cover(files['cover'])
        book.update_series(form['series'], form['series_seq'])
        book.update_tags(form['tags'])
        db.session.commit()
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
    authors = set()

    books = get_books();
    for book in books:
        authors.add(book.author)

    return authors


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
