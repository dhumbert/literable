from flask import render_template, request, redirect, url_for, flash, abort
from literable import app, model, admin_required


@app.route("/admin/books/all")
@admin_required
def admin_books_all():
    books = model.get_all_books()
    return render_template('admin/all.html', books=books, num_books=len(books))

@app.route("/admin/books/incomplete")
@admin_required
def admin_books_incomplete():
    incomplete = model.get_incomplete_books()
    return render_template('admin/incomplete.html', incomplete=incomplete)


@app.route("/admin/taxonomies")
@admin_required
def admin_taxonomies():
    taxonomies = model.get_taxonomies_and_terms()
    return render_template('admin/taxonomies.html', taxonomies=taxonomies, generate_hierarchical_list=model.generate_genre_tree_list, hierarchical_select=model.generate_genre_tree_select_options(value_id=True))


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
