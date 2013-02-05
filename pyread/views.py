import json
from flask import render_template, request, redirect, url_for, flash
from pyread import app, model, content_type


@app.route("/")
def list_books():
    books = model.get_books()
    return render_template('books/list.html', books=books)


@app.route("/books/add")
def add_book():
    book = model.get_book(None)  # blank book obj for form
    return render_template('books/add.html', book=book, genre_select=model.generate_genre_tree_select)


@app.route("/books/add", methods=['POST'])
def add_book_post():
    if model.add_book(request.form, request.files):
        return redirect(url_for('list_books'))


@app.route("/books/download/<int:id>")
def download_book(id):
    return model.download_book(id)


@app.route("/books/edit/<int:id>")
def edit_book(id):
    book = model.get_book(id)
    if book:
        return render_template('books/edit.html', book=book, genre_select=model.generate_genre_tree_select)


@app.route("/books/edit/<int:id>", methods=['POST'])
def edit_book_do(id):
    if model.edit_book(id, request.form, request.files):
        flash('Your changes were saved', 'success')
    else:
        flash('Error saving changes', 'error')

    return redirect(url_for('edit_book', id=id))


@app.route("/tags")
def list_tags():
    tags = model.get_tags()
    return render_template('tags/list.html', tags=tags)


@app.route("/tags/<tag>")
def tag(tag):
    books, tag = model.get_books_by_tag(tag)
    return render_template('books/list.html', books=books, tag=tag)


@app.route("/genres")
def list_genres():
    genres = model.get_genres()
    return render_template('genres/list.html', genres=genres)


@app.route("/genre/<genre>")
def genre(genre):
    books, genre = model.get_books_by_genre(genre)
    return render_template('books/list.html', books=books, genre=genre)


@app.route("/ajax/tags")
@content_type("application/json")
def ajax_tags():
    tags = model.get_tags()
    names = [tag.name for tag in tags]
    return json.dumps(names)
