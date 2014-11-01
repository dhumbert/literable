import json
from flask import render_template, request
from flask.ext.login import login_required, current_user
from literable import app, model


@app.route("/reading-list")
@login_required
def reading_list():
    books = current_user.reading_list
    return render_template('books/list.html', books=books, reading_list=True)


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