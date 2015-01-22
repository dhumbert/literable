import json
from flask import render_template, request, redirect, url_for, flash, abort
from flask.ext.login import login_required, current_user
from literable import app, model


@app.route("/reading-lists")
@app.route("/reading-lists/<rlist>")
@login_required
def reading_lists(rlist='Default List'):
    current_list = current_user.get_reading_list(rlist)

    title = u'{} | Reading Lists'.format(current_list.name)

    sort = request.args.get('sort', 'created')
    sort_dir = request.args.get('dir', 'desc')

    sort_key = 'created_at' if sort == 'created' else sort
    reverse = True if sort_dir == 'desc' else False
    books = sorted(current_list.books, key=lambda x: getattr(x, sort_key), reverse=reverse)

    return render_template('books/list.html',
                           reading_list=current_list, books=books,
                           title=title, sort=sort, dir=sort_dir)


@app.route("/reading-lists", methods=['POST'])
def new_reading_list():
    next_page = request.form.get('next')
    name = request.form.get('name')

    model.new_reading_list(name)

    flash('Created list "{}"'.format(name), 'success')

    if next_page:
        return redirect(next_page)
    else:
        return redirect(url_for('recent'))


@app.route("/delete-reading-list/<list_id>")
def delete_reading_list(list_id):
    try:
        model.delete_reading_list(list_id)
    except Exception as e:
        print e
        abort(403)

    flash('Deleted reading list', 'success')
    return redirect(url_for('recent'))




@app.route("/ajax/order_reading_list", methods=['POST'])
@login_required
def order_reading_list():
    model.update_reading_list_order(request.form['list_id'], json.loads(request.form['data']))
    return json.dumps(True)


@app.route("/ajax/add_to_reading_list", methods=['POST'])
@login_required
def add_to_reading_list():
    model.add_to_reading_list(request.form['list_id'], request.form['book_id'])
    return json.dumps(True)


@app.route("/ajax/remove_from_reading_list", methods=['POST'])
@login_required
def remove_from_reading_list():
    model.remove_from_reading_list(request.form['list_id'], request.form['book_id'])
    return json.dumps(True)