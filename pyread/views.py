from flask import render_template, request
from pyread import app, model


@app.route("/")
def list_books():
    books = model.get_books()
    return render_template('books/list.html', books=books)


@app.route("/books/add")
def add_book():
    return render_template('books/add.html')


@app.route("/books/add", methods=['POST'])
def add_book_post():
    attrs = (request.form['title'], request.form['author'], request.files['file'])
    if model.save_book(attrs):
        pass

    return 'asdf'