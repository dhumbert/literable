import json
from flask import render_template, request, redirect, url_for, flash, Response
from seshat import app, model, content_type, auth


@app.route("/")
@auth.requires_auth
def list_books():
    books = model.get_books()
    return render_template('books/list.html', books=books)


@app.route("/books/add")
@auth.requires_auth
def add_book():
    book = model.get_book(None)  # blank book obj for form
    return render_template('books/add.html', book=book, genre_options=model.generate_genre_tree_select_options)


@app.route("/books/add", methods=['POST'])
@auth.requires_auth
def add_book_post():
    if model.add_book(request.form, request.files):
        return redirect(url_for('list_books'))


@app.route("/books/download/<int:id>")
@auth.requires_auth
@content_type('application/octet-stream')
def download_book(id):
    book = model.get_book(id)
    response = Response()
    # todo: there has to be a better way to do this.
    # book_upload_set.url doesn't generate the right URL for nginx
    response.headers['X-Accel-Redirect'] = app.config['UPLOADS_DEFAULT_URL'] + 'library/' + book.filename
    response.headers['Content-Disposition'] = 'attachment; filename=%s' % book.filename
    return response


@app.route("/books/edit/<int:id>")
@auth.requires_auth
def edit_book(id):
    book = model.get_book(id)
    if book:
        return render_template('books/edit.html', book=book, genre_options=model.generate_genre_tree_select_options)


@app.route("/books/edit/<int:id>", methods=['POST'])
@auth.requires_auth
def edit_book_do(id):
    if model.edit_book(id, request.form, request.files):
        flash('Your changes were saved', 'success')
    else:
        flash('Error saving changes', 'error')

    return redirect(url_for('edit_book', id=id))


@app.route("/books/delete/<int:id>")
@auth.requires_auth
def delete_book(id):
    model.delete_book(id)
    flash('Book deleted', 'success')
    return redirect(url_for('list_books'))


@app.route("/tags")
@auth.requires_auth
def list_tags():
    tags = model.get_tags()
    return render_template('tags/list.html', tags=tags)


@app.route("/tags/<tag>")
@auth.requires_auth
def tag(tag):
    books, tag = model.get_books_by_tag(tag)
    return render_template('books/list.html', books=books, tag=tag)


@app.route("/genres")
@auth.requires_auth
def list_genres():
    genre_list = model.generate_genre_tree_list
    return render_template('genres/list.html', genre_list=genre_list)


@app.route("/genre/<genre>")
@auth.requires_auth
def genre(genre):
    books, genre = model.get_books_by_genre(genre)
    return render_template('books/list.html', books=books, genre=genre)


@app.route("/ajax/tags")
@content_type("application/json")
@auth.requires_auth
def ajax_tags():
    tags = model.get_tags()
    names = [tag.name for tag in tags]
    return json.dumps(names)
