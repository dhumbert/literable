from flask import render_template, request
from flask.ext.login import login_required
from literable import app, model


@app.route("/search")
@login_required
def search():
    term = request.args.get('q')
    if not term:
        term = ""
    books = model.search_books(term)
    return render_template('books/list.html', books=books, search=term)