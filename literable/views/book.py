import json
from flask import render_template, request, redirect, url_for, flash, Response, abort
from flask.ext.login import login_required, current_user
from literable import app, model, content_type


@app.route("/")
@app.route("/books")
@app.route("/recent")
@login_required
def recent():
    page = request.args.get('page')
    title = 'Recent Books | Page {}'.format(max(page, 1))
    books = model.get_recent_books(page)
    return render_template('books/list.html', books=books, recent=True,
                           title=title, pagination='books/pagination_recent.html')


@app.route("/rated")
def rated():
    title = 'Rated Books'
    books = current_user.rated_books
    return render_template('books/list.html', books=books, rated=True, title=title)

@app.route("/books/add")
@login_required
def add_book():
    title = 'Add Book'
    book = model.get_book(None)  # blank book obj for form

    return render_template('books/add.html', book=book, new=True,
                           series=request.args.get('series'),
                           series_seq=request.args.get('series_seq'),
                           genre=request.args.get('genre'),
                           genre_options=model.generate_genre_tree_select_options,
                           title=title)


@app.route("/books/add", methods=['POST'])
@login_required
def add_book_post():
    try:
        model.add_book(request.form, request.files)
        flash('Added book', 'success')

        if 'post-submit-action' in request.form and request.form['post-submit-action']:
            if request.form['post-submit-action'] == 'add_another':
                return redirect(url_for('add_book'))
            elif request.form['post-submit-action'] == 'add_next_in_series':
                if request.form['series_seq']:
                    seq = int(request.form['series_seq']) + 1
                else:
                    seq = None
                return redirect(url_for('add_book', series=request.form['series'], series_seq=seq, genre=request.form['genre']))
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
        title = u'{} | Edit'.format(book.title)
        return render_template('books/edit.html', book=book, new=False,
                               genre_options=model.generate_genre_tree_select_options,
                               title=title)


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


@app.route("/ajax/rate", methods=['POST'])
@login_required
def ajax_rate():
    score = request.form['score']
    book_id = request.form['book_id']

    model.rate_book(book_id, score)
    return json.dumps(True)