from flask import render_template, request
from flask.ext.login import current_user

from literable import model, basic_auth
from literable.modules.opds import opds_module


@opds_module.route('/catalog.atom')
@basic_auth
def index():
    return render_template('catalog.xml')


@opds_module.route('/recent.atom')
@basic_auth
def recent():
    page = request.args.get('page')
    books = model.get_recent_books(page, 'created', 'desc')
    return render_template('recent.xml', books=books)


@opds_module.route('/lists.atom')
@basic_auth
def lists():
    reading_lists = current_user.reading_lists
    return render_template('lists.xml', lists=reading_lists)


@opds_module.route('/list.atom')
@basic_auth
def list():
    current_list = current_user.get_reading_list_by_id(int(request.args.get('id')))
    return render_template('list.xml', list=current_list)


@opds_module.route('/search-manifest.xml')
@basic_auth
def search_manifest():
    return render_template('search_manifest.xml')


@opds_module.route('/search.atom')
@basic_auth
def search():
    books = model.search_books(request.args.get('q'))
    return render_template('recent.xml', books=books)
