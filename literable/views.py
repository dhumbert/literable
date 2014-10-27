import json
from flask import render_template, request, redirect, url_for, flash, Response, abort
from flask.ext.login import login_required, login_user, logout_user, current_user
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
    return render_template('books/add.html', book=book, new=True, genre_options=model.generate_genre_tree_select_options)


@app.route("/books/add", methods=['POST'])
@login_required
def add_book_post():
    try:
        model.add_book(request.form, request.files)
        return redirect(url_for('recent'))
    except ValueError as e:
        flash(e, 'error')
        return redirect(url_for('add_book'))


@app.route("/books/upload", methods=['POST'])
@login_required
@content_type("application/json")
def upload_book():
    try:
        filename, meta = model.upload_book(request.files['Filedata'])
        if not filename:
            raise Exception("Unable to upload book")
    except Exception as e:
        app.logger.exception(e)
        abort(500)

    results = {
        'filename': filename,
        'meta': meta,
    }

    return json.dumps(results)


@app.route("/books/download/<int:id>")
@login_required
@content_type('application/octet-stream')
def download_book(id):
    book = model.get_book(id)

    if not model.user_can_download_book(book, current_user):
        abort(403)

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
        if not model.user_can_modify_book(book, current_user):
            abort(403)
        return render_template('books/edit.html', book=book, new=False, genre_options=model.generate_genre_tree_select_options)


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
        if not url:
            url = url_for('recent')
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


@app.route("/reading-list")
@login_required
def reading_list():
    books = current_user.reading_list
    return render_template('books/list.html', books=books, reading_list=True)


@app.route("/t/<ttype>/<slug>")
@login_required
def taxonomy(ttype, slug):
    books, tax = model.get_taxonomy_books(ttype, slug, page=request.args.get('page'))
    return render_template('books/list.html', books=books, taxonomy=tax, pagination='taxonomies/pagination.html')


@app.route("/t/<ttype>", methods=["GET", "POST"])
@login_required
def taxonomy_terms(ttype):
    if request.method == 'POST':
        #model.delete_tax('author', request.form.getlist('delete'))
        flash('Deleted {}(s)'.format(ttype), 'success')
        return redirect(url_for('taxonomy_terms', ttype=ttype))

    order = request.args.get('order')

    terms = model.get_taxonomy_terms_and_counts(ttype, order)
    return render_template('taxonomies/list.html', ttype=ttype, terms=terms, order=order)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = model.authenticate(request.form['username'], request.form['password'])
        if user:
            login_user(user, remember=True)
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
    if not term:
        term = ""
    books = model.search_books(term)
    return render_template('books/list.html', books=books, search=term)


@app.route("/ajax/taxonomy/<ttype>")
@content_type("application/json")
@login_required
def ajax_taxonomy(ttype):
    terms = model.get_taxonomy_terms(ttype)
    names = [term.name for term in terms]
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