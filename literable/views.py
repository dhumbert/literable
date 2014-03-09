import json
from flask import render_template, request, redirect, url_for, flash, Response
from flask.ext.login import login_required, login_user, logout_user, current_user
from functools import partial
from literable import app, model, content_type


app.jinja_env.globals['is_book_in_reading_list'] = model.is_book_in_reading_list

@app.route("/")
@app.route("/books")
@app.route("/recent")
@login_required
def recent():
    books = model.get_recent_books(request.args.get('page'))
    return render_template('books/list.html', books=books, recent=True, pagination='books/pagination_recent.html')


@app.route("/books/add")
@login_required
def add_book():
    book = model.get_book(None)  # blank book obj for form
    return render_template('books/add.html', book=book, genre_options=model.generate_genre_tree_select_options)


@app.route("/books/add", methods=['POST'])
@login_required
def add_book_post():
    try:
        model.add_book(request.form, request.files)
        return redirect(url_for('recent'))
    except ValueError as e:
        flash(e, 'error')
        return redirect(url_for('add_book'))


@app.route("/books/download/<int:id>")
@login_required
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
@login_required
def edit_book(id):
    book = model.get_book(id)
    if book:
        return render_template('books/edit.html', book=book, genre_options=model.generate_genre_tree_select_options)


@app.route("/books/edit/<int:id>", methods=['POST'])
@login_required
def edit_book_do(id):
    if model.edit_book(id, request.form, request.files):
        flash('Your changes were saved', 'success')
    else:
        flash('Error saving changes', 'error')

    return redirect(url_for('edit_book', id=id))


@app.route("/books/delete/<int:id>")
@login_required
def delete_book(id):
    model.delete_book(id)
    flash('Book deleted', 'success')
    try:
        url = request.args.get('next')
    except KeyError:
        url = url_for('recent')
    return redirect(url)


@app.route("/books/write-meta/<int:id>")
@login_required
def write_book_meta(id):
    book = model.get_book(id)
    book.write_meta()
    flash('Saved file metadata', 'success')
    return redirect(url_for('edit_book', id=id))

@app.route("/tags", methods=["GET", "POST"])
@login_required
def list_tags():
    if request.method == 'POST':
        model.delete_tax('tag', request.form.getlist('delete'))
        flash('Deleted tag(s)', 'success')
        return redirect(url_for('list_tags'))

    tags = model.get_tags()
    return render_template('tags/list.html', tags=tags)


@app.route("/tags/<tag>")
@login_required
def tag(tag):
    books, tag = model.get_books_by_tag(tag, request.args.get('page'))
    return render_template('books/list.html', books=books, tag=tag, pagination='tags/pagination.html')


@app.route("/genres", methods=["GET", "POST"])
@login_required
def list_genres():
    if request.method == 'POST':
        model.delete_tax('genre', request.form.getlist('delete'))
        flash('Deleted genre(s)', 'success')
        return redirect(url_for('list_genres'))
    genre_list = model.generate_genre_tree_list
    return render_template('genres/list.html', genre_list=genre_list)


@app.route("/genre/<genre>")
@login_required
def genre(genre):
    books, genre = model.get_books_by_genre(genre, request.args.get('page'))
    return render_template('books/list.html', books=books, genre=genre, pagination='genres/pagination.html')


@app.route("/series", methods=["GET", "POST"])
@login_required
def list_series():
    if request.method == 'POST':
        model.delete_tax('series', request.form.getlist('delete'))
        flash('Deleted series', 'success')
        return redirect(url_for('list_series'))

    series = model.get_series()
    return render_template('series/list.html', series=series)


@app.route("/series/<series>")
@login_required
def series(series):
    books, series = model.get_books_by_series(series, request.args.get('page'))
    return render_template('books/list.html', books=books, series=series, pagination='series/pagination.html')


@app.route("/author/<author>")
@login_required
def author(author):
    books, author = model.get_books_by_author(author, request.args.get('page'))
    return render_template('books/list.html', books=books, author=author, pagination='authors/pagination.html')


@app.route("/reading-list")
@login_required
def reading_list():
    books = current_user.reading_list
    return render_template('books/list.html', books=books, reading_list=True)


@app.route("/authors", methods=["GET", "POST"])
@login_required
def list_authors():
    if request.method == 'POST':
        model.delete_tax('author', request.form.getlist('delete'))
        flash('Deleted author(s)', 'success')
        return redirect(url_for('list_authors'))

    authors = model.get_authors()
    return render_template('authors/list.html', authors=authors)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = model.authenticate(request.form['username'], request.form['password'])
        if user:
            login_user(user)
            url = request.form['next'] if 'next' in request.form else '/'
            return redirect(url)
        else:
            flash('Invalid login', 'error')
            return redirect('/login')
    return render_template('users/login.html', next=request.args.get('next'))


@app.route("/logout")
def logout():
    logout_user()
    return redirect('/login')


@app.route("/search")
@login_required
def search():
    term = request.args.get('q')
    books = model.search_books(term, request.args.get('page'))
    return render_template('books/list.html', books=books, search=term, pagination='books/pagination_search.html')

@app.route("/ajax/tags")
@content_type("application/json")
@login_required
def ajax_tags():
    tags = model.get_tags()
    names = [tag.name for tag in tags]
    return json.dumps(names)


@app.route("/ajax/series")
@content_type("application/json")
@login_required
def ajax_series():
    series = model.get_series()
    titles = [sery.title for sery in series]
    return json.dumps(titles)


@app.route("/ajax/author")
@content_type("application/json")
@login_required
def ajax_author():
    authors = model.get_authors()
    names = [author.name for author in authors]
    return json.dumps(names)


@app.route("/ajax/rate", methods=['POST'])
@login_required
def ajax_rate():
    score = request.form['score']
    book_id = request.form['book_id']
    book = model.get_book(book_id)
    book.rate(score)
    return json.dumps(True)


@app.route("/ajax/order_reading_list", methods=['POST'])
@login_required
def order_reading_list():
    model.update_reading_list_order(current_user, json.loads(request.form['data']))
    return json.dumps(True)


@app.route("/ajax/add_to_reading_list", methods=['POST'])
@login_required
def add_to_reading_list():
    model.add_to_reading_list(current_user, request.form['book_id'])
    return json.dumps(True)


@app.route("/ajax/remove_from_reading_list", methods=['POST'])
@login_required
def remove_from_reading_list():
    model.remove_from_reading_list(current_user, request.form['book_id'])
    return json.dumps(True)