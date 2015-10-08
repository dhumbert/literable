from flask import render_template, request

from literable import model, basic_auth
from literable.modules.opds import opds_module


@opds_module.route('/')
@opds_module.route('/recent.atom')
@basic_auth
def index():
    page = request.args.get('page')
    books = model.get_recent_books(page, 'created', 'desc')
    return render_template('feed.xml', books=books)


@opds_module.route('/search-manifest.xml')
@basic_auth
def search_manifest():
    return render_template('search_manifest.xml')


@opds_module.route('/search.atom')
@basic_auth
def search():
    books = model.search_books(request.args.get('q'))
    return render_template('feed.xml', books=books)
