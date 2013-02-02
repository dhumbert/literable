from flask import render_template, request, redirect, url_for
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
    attrs = (request.form['title'], request.form['author'], request.files['file'], request.files['cover'])
    if model.save_book(attrs):
        return redirect(url_for('list_books'))


@app.route("/books/download/<int:id>")
def download_book(id):
    return model.download_book(id)
