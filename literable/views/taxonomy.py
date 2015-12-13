import json
from flask import render_template, request, redirect, url_for, flash
from flask.ext.login import login_required
from literable import app, model, content_type


@app.route("/t/<ttype>/<slug>")
@login_required
def taxonomy(ttype, slug):
    page = request.args.get('page')
    sort = request.args.get('sort', 'created')
    sort_dir = request.args.get('dir', 'desc')

    books, tax = model.get_taxonomy_books(ttype, slug, page=page, sort=sort, sort_dir=sort_dir)
    title = u'{} | {} | Taxonomies'.format(tax.name, tax.type.title())
    return render_template('books/list.html', books=books, taxonomy=tax,
                           sort=sort, dir=sort_dir,
                           pagination_page='taxonomy',
                           pagination_args={'ttype': ttype, 'slug': slug},
                           title=title)


@app.route("/t/<ttype>", methods=["GET", "POST"])
@login_required
def taxonomy_terms(ttype):
    if request.method == 'POST':
        #model.delete_tax('author', request.form.getlist('delete'))
        flash('Deleted {}(s)'.format(ttype), 'success')
        return redirect(url_for('taxonomy_terms', ttype=ttype))

    order = request.args.get('order')

    terms = model.get_taxonomy_terms_and_counts(ttype, order)
    title = u'{} | Taxonomies'.format(ttype.title())
    return render_template('taxonomies/list.html', ttype=ttype, terms=terms,
                           order=order,
                           title=title)


@app.route("/ajax/taxonomy/<ttype>")
@content_type("application/json")
@login_required
def ajax_taxonomy(ttype):
    terms = model.get_taxonomy_terms(ttype)
    names = [term.name for term in terms]
    return json.dumps(names)
