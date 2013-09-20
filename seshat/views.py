import json
from flask import render_template, request, redirect, url_for, flash, Response
from seshat import app, model, content_type, auth


@app.route("/")
@app.route("/books")
@auth.requires_auth
def list_books():
    books = model.get_books(request.args.get('page'))
    return render_template('books/list.html', books=books, pagination='books/pagination.html')


@app.route("/books/add")
@auth.requires_auth
def add_book():
    book = model.get_book(None)  # blank book obj for form
    return render_template('books/add.html', book=book, genre_options=model.generate_genre_tree_select_options)


@app.route("/books/add", methods=['POST'])
@auth.requires_auth
def add_book_post():
    try:
        model.add_book(request.form, request.files)
        return redirect(url_for('list_books'))
    except ValueError as e:
        flash(e, 'error')
        return redirect(url_for('add_book'))


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


@app.route("/books/write-meta/<int:id>")
@auth.requires_auth
def write_book_meta(id):
    book = model.get_book(id)
    book.write_meta()
    flash('Saved file metadata', 'success')
    return redirect(url_for('edit_book', id=id))

@app.route("/tags")
@auth.requires_auth
def list_tags():
    tags = model.get_tags()
    return render_template('tags/list.html', tags=tags)


@app.route("/tags/<tag>")
@auth.requires_auth
def tag(tag):
    books, tag = model.get_books_by_tag(tag, request.args.get('page'))
    return render_template('books/list.html', books=books, tag=tag, pagination='tags/pagination.html')


@app.route("/genres")
@auth.requires_auth
def list_genres():
    genre_list = model.generate_genre_tree_list
    return render_template('genres/list.html', genre_list=genre_list)


@app.route("/genre/<genre>")
@auth.requires_auth
def genre(genre):
    books, genre = model.get_books_by_genre(genre, request.args.get('page'))
    return render_template('books/list.html', books=books, genre=genre, pagination='genres/pagination.html')


@app.route("/series")
@auth.requires_auth
def list_series():
    series = model.get_series()
    return render_template('series/list.html', series=series)


@app.route("/series/<series>")
@auth.requires_auth
def series(series):
    books, series = model.get_books_by_series(series, request.args.get('page'))
    return render_template('books/list.html', books=books, series=series, pagination='series/pagination.html')


@app.route("/author/<author>")
@auth.requires_auth
def author(author):
    books, author = model.get_books_by_author(author, request.args.get('page'))
    return render_template('books/list.html', books=books, author=author, pagination='authors/pagination.html')


@app.route("/authors")
@auth.requires_auth
def list_authors():
    authors = model.get_authors()
    return render_template('authors/list.html', authors=authors)

@app.route("/recent")
@auth.requires_auth
def recent():
    books = model.get_recent_books(request.args.get('page'))
    return render_template('books/list.html', books=books, recent=True, pagination='books/pagination_recent.html')


@app.route("/ajax/tags")
@content_type("application/json")
@auth.requires_auth
def ajax_tags():
    tags = model.get_tags()
    names = [tag.name for tag in tags]
    return json.dumps(names)


@app.route("/ajax/series")
@content_type("application/json")
@auth.requires_auth
def ajax_series():
    series = model.get_series()
    titles = [sery.title for sery in series]
    return json.dumps(titles)


@app.route("/ajax/author")
@content_type("application/json")
@auth.requires_auth
def ajax_author():
    authors = model.get_authors()
    names = [author.name for author in authors]
    return json.dumps(names)


@app.route("/ajax/rate", methods=['POST'])
@auth.requires_auth
def ajax_rate():
    score = request.form['score']
    book_id = request.form['book_id']
    book = model.get_book(book_id)
    book.rate(score)
    return json.dumps(True)

