from flask import render_template, request, redirect, url_for, flash, abort
from literable import app, model, admin_required


@app.route("/admin/books/all")
@admin_required
def admin_books_all():
    books = model.get_all_books()
    title = 'All Books | Admin'
    return render_template('admin/all.html', books=books, num_books=len(books),
                           title=title)

@app.route("/admin/books/incomplete")
@admin_required
def admin_books_incomplete():
    incomplete = model.get_incomplete_books()
    title = 'Incomplete Books | Admin'
    return render_template('admin/incomplete.html', incomplete=incomplete,
                           title=title)


@app.route("/admin/books/covers")
@admin_required
def admin_covers():
    covers = model.get_book_covers()
    title = 'Book Covers | Admin'
    return render_template('admin/covers.html', covers=covers,
                           title=title)


@app.route("/admin/taxonomies")
@admin_required
def admin_taxonomies():
    taxonomies = model.get_taxonomies_and_terms()
    title = 'Taxonomies | Admin'
    return render_template('admin/taxonomies.html', taxonomies=taxonomies, title=title)


@app.route("/admin/taxonomies/edit", methods=['POST'])
@admin_required
def admin_taxonomy_edit():
    action = request.form['action']
    result = None

    if action == 'Save Term':
        result = model.edit_taxonomy(request.form)
    elif action == 'Delete Term':
        result = model.delete_taxonomy(request.form)
    else:
        abort(400)

    if result:
        flash('Updated term', 'success')
    else:
        flash('Unable to update term', 'error')

    return redirect(url_for('admin_taxonomies'))


@app.route("/admin/books/calibre-id", methods=['GET', 'POST'])
@admin_required
def admin_bulk_calibre_id():
    books = model.get_all_books()

    if request.method == 'POST':
        for book in books:
            book.id_isbn = request.form.get('id_isbn_' + str(book.id))
            book.id_calibre = request.form.get('id_calibre_' + str(book.id))

        model.save_updated_books(books)


        flash('Saved Identifiers', 'success')
        return redirect(url_for('admin_bulk_calibre_id'))
    else:
        return render_template('admin/bulk_calibre_id.html', books=books)