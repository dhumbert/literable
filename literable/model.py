from datetime import datetime
import hashlib
import os
import os.path
from flask import url_for, flash
from flask.ext.login import current_user
from sqlalchemy import or_, and_
from sqlalchemy.exc import IntegrityError
from elasticutils import S, get_es
from literable import db, app, book_staging_upload_set, tmp_cover_upload_set, epub
from literable.orm import Book, User, ReadingList, Taxonomy


def _get_page(page):
    if page is None:
        page = 1
    else:
        page = int(page)
    return page


def _privilege_filter():
    return or_(current_user.admin, Book.user_id == current_user.id, Book.public)


def user_can_modify_book(book, user):
    return user.admin or book.user_id == current_user.id


def user_can_download_book(book, user):
    return book.public or user_can_modify_book(book, user)


def get_books(page):
    page = max(1, _get_page(page))
    return Book.query.order_by(Book.title).paginate(page, per_page=app.config['BOOKS_PER_PAGE'])


def get_all_books():
    return Book.query.order_by(Book.title).all()


def get_book(id):
    if id is None:
        return Book()  # blank book object
    else:
        return Book.query.get_or_404(id)


def get_recent_books(page):
    page = max(1, _get_page(page))
    return Book.query.filter(_privilege_filter()).order_by('created_at desc, id desc').paginate(page, per_page=app.config['BOOKS_PER_PAGE'])


def search_books(q):
    if app.config['ELASTICSEARCH_ENABLED']:
        return _search_books_elasticsearch(q)
    else:
        return Book.query.filter(and_(Book.title.ilike("%"+q+"%"), _privilege_filter())).order_by('created_at desc, id desc')


def _search_books_elasticsearch(q):
    searcher = S()\
        .es(urls=app.config['ELASTICSEARCH_NODES'])\
        .indexes(app.config['ELASTICSEARCH_INDEX'])\
        .query(_all__match=q)\
        .highlight('*', pre_tags=['<span class="highlight">'], post_tags=["</span>"], number_of_fragments=0)  # number_of_fragments=0 means the entire field will be returned, not just highlighted snippets

    # searcher = searcher[0:searcher.count()]  # get all  = searcher

    found_ids = []
    highlights = {}

    results = list(searcher.values_dict('title', 'id', 'author'))
    for result in results:
        # can't find a way to do this with elasticutils, though ES does support min_score.
        if result.es_meta.score < 0.25:
            continue

        book_id = result['id'][0]

        found_ids.append(book_id)

        r = {}
        for field, highlight in result.es_meta.highlight.iteritems():
            r[field] = highlight[0]

        if r:
            highlights[book_id] = r

    books = []
    for id in found_ids:
        book = Book.query.get(id)

        if id in highlights:
            if 'title' in highlights[id]:
                book.title = highlights[id]['title']

            if 'description' in highlights[id]:
                book.description = highlights[id]['description']

        books.append(book)

    # todo privilege filter
    return books


def get_incomplete_books():
    books = {
        'without a cover': [],
        'without a description': [],
        'without a file': [],
        'without an author': [],
        'without a genre': [],
        'without a publisher': [],
    }

    for book in get_all_books():
        if not book.authors:
            books['without an author'].append(book)
        if not book.cover:
            books['without a cover'].append(book)
        if not book.filename:
            books['without a file'].append(book)
        if not book.description:
            books['without a description'].append(book)
        if not book.genres:
            books['without a genre'].append(book)
        if not book.publishers:
            books['without a publisher'].append(book)

    return books

def get_taxonomy_books(tax_type, tax_slug, page=None):
    page = max(1, _get_page(page))

    tax = Taxonomy.query.filter_by(type=tax_type, slug=tax_slug).first_or_404()
    books = Book.query.filter(and_(Book.taxonomies.any(Taxonomy.id == tax.id), _privilege_filter())).order_by(Book.title).paginate(page, per_page=app.config['BOOKS_PER_PAGE'])
    books = None if len(books.items) == 0 else books

    return (books, tax)


def get_taxonomy_terms(ttype):
    return Taxonomy.query.filter_by(type=ttype).order_by(Taxonomy.name)


def get_taxonomy_terms_and_counts(ttype, order=None):
    return Taxonomy.get_grouped_counts(ttype, order)


def get_taxonomy_types():
    return Taxonomy.get_types()


def get_taxonomies_and_terms():
    taxonomies = {}
    for ttype, hierarchical in get_taxonomy_types().iteritems():
        terms = get_taxonomy_terms_and_counts(ttype)

        taxonomies[ttype] = {
            'hierarchical': hierarchical,
            'terms': terms
        }
    # for tax in Taxonomy.query.order_by(Taxonomy.name).all():
    #     if tax.type not in taxonomies:
    #         taxonomies[tax.type] = {'hierarchical': False, 'terms': []}
    #
    #     taxonomies[tax.type]['terms'].append(tax)
    #
    #     if tax.parent_id and not taxonomies[tax.type]['hierarchical']:
    #         taxonomies[tax.type]['hierarchical'] = True

    return taxonomies


def add_book(form, files):
    if 'title' not in form or not form['title'].strip():
        raise ValueError("Title must not be blank")

    book = Book()
    book.title = form['title']
    book.description = form['description']
    book.series_seq = int(form['series_seq']) if form['series_seq'] else None
    book.public = True if form['privacy'] == 'public' else False
    book.user = current_user
    book.created_at = datetime.now()

    book.update_taxonomies({
        'author': [form['author']],
        'publisher': [form['publisher']],
        'series': [form['series']],
        'genre': [form['genre']],
        'tag': form['tags'].split(','),
    })

    if 'meta-cover' in form and form['meta-cover']:
        book.move_cover_from_tmp(form['meta-cover'])
    elif 'cover' in files:
        book.attempt_to_update_cover(files['cover'])

    if 'file' in form and form['file']:
        book.move_file_from_staging(form['file'])

    db.session.add(book)
    db.session.commit()

    if app.config['WRITE_META_ON_SAVE']:
        book.write_meta()

    book_to_elasticsearch(book)

    return True


def edit_book(id, form, files):
    book = get_book(id)
    if book:
        if not user_can_modify_book(book, current_user):
            return False

        book.title = form['title']
        book.description = form['description']
        book.series_seq = int(form['series_seq']) if form['series_seq'] else None
        book.public = True if form['privacy'] == 'public' else False

        book.update_taxonomies({
            'author': [form['author']],
            'publisher': [form['publisher']],
            'series': [form['series']],
            'genre': [form['genre']],
            'tag': form['tags'].split(','),
        })

        if 'meta-cover' in form and form['meta-cover']:
            book.move_cover_from_tmp(form['meta-cover'])
        elif 'cover' in files and files['cover']:
            book.attempt_to_update_cover(files['cover'])

        if 'file' in form and form['file']:
            book.move_file_from_staging(form['file'])

        db.session.commit()

        if app.config['WRITE_META_ON_SAVE']:
            book.write_meta()

        book_to_elasticsearch(book)

        return True
    return False


def upload_book(file):
    filename = book_staging_upload_set.save(file)
    if filename:
        extension = os.path.splitext(filename)[1][1:]
        if extension == 'epub':
            e = epub.Epub(book_staging_upload_set.path(filename))
            if e:
                meta = e.metadata
                meta['author'] = meta['creator']
                del meta['creator']

                # if the book has a cover, copy it to tmp directory
                if e.cover:
                    cover_filename = os.path.basename(e.cover)
                    # todo conflicts
                    if os.path.exists(tmp_cover_upload_set.path(cover_filename)):
                        cover_filename = tmp_cover_upload_set.resolve_conflict(tmp_cover_upload_set.config.destination, cover_filename)

                    dest = tmp_cover_upload_set.path(cover_filename)
                    extracted = e.extract_cover(dest)

                    if extracted:
                        meta['cover'] = cover_filename
            else:
                meta = None
        else:
            meta = None

        return filename, meta
    else:
        return None


def book_to_elasticsearch(book):
    if app.config['ELASTICSEARCH_ENABLED']:
        es_doc = {'title': book.title,
                  'description': book.description,
                  'id': book.id,
                  }
        if book.series:
            es_doc['series'] = book.series[0].name

        if book.authors:
            es_doc['author'] = book.authors[0].name

        es = get_es(urls=app.config['ELASTICSEARCH_NODES'])
        es.index(app.config['ELASTICSEARCH_INDEX'],
                 app.config['ELASTICSEARCH_DOC_TYPE'],
                 body=es_doc,
                 id=book.id)


def delete_from_elasticsearch(book):
    if app.config['ELASTICSEARCH_ENABLED']:
        es = get_es(urls=app.config['ELASTICSEARCH_NODES'])
        try:
            es.delete(app.config['ELASTICSEARCH_INDEX'],
                     app.config['ELASTICSEARCH_DOC_TYPE'],
                     id=book.id)
        except Exception as e:
            app.logger.warning("Unable to delete book from ES: {}".format(e.message))


def delete_book(id):
    book = get_book(id)

    if not user_can_modify_book(book, current_user):
        flash('You cannot delete a book you do not own', 'error')
        return False

    try:
        book.remove_file()
    except:
        flash('Unable to delete file', 'error')

    try:
        book.remove_cover()
    except:
        flash('Unable to delete cover', 'error')

    db.session.delete(book)
    db.session.commit()

    delete_from_elasticsearch(book)


def get_taxonomy_terms_without_parent(ttype):
    return Taxonomy.query.filter_by(parent_id=None, type=ttype).order_by(Taxonomy.name).all()


def add_taxonomy(name, ttype, parent=None):
    tax = Taxonomy()
    tax.name = name
    tax.slug = tax.generate_slug()
    tax.type = ttype
    tax.parent_id = parent if parent else None
    db.session.add(tax)
    db.session.commit()
    return tax.id


def edit_taxonomy(data):
    if 'id' not in data:
        return False

    tax = Taxonomy.query.get(data['id'])
    if not tax:
        return False

    tax.name = data['name']
    tax.slug = tax.generate_slug()

    if 'parent' in data and data['parent']:
        tax.parent_id = int(data['parent'])
    else:
        tax.parent_id = None

    db.session.commit()

    return True


def delete_taxonomy(data):
    if 'id' not in data:
        return False

    tax = Taxonomy.query.get(data['id'])
    if not tax:
        return False

    db.session.delete(tax)
    db.session.commit()
    return True


def delete_tax_if_possible(tax, id):
    pass
    # obj = {
    #     'genre': Genre,
    #     'tag': Tag,
    #     'series': Series,
    #     'author': Author,
    #     'publisher': Publisher,
    # }[tax]
    #
    # instance = obj.query.get(int(id))
    # if instance:
    #     if len(instance.books) == 0:  # no books left, so we can delete
    #         delete_tax(tax, [id])


def delete_tax(tax, ids):
    pass
    # obj = {
    #     'genre': Genre,
    #     'tag': Tag,
    #     'series': Series,
    #     'author': Author,
    #     'publisher': Publisher,
    # }[tax]
    #
    # for id in ids:
    #     t = obj.query.get(int(id))
    #     db.session.delete(t)
    #
    # db.session.commit()


def add_user(username, password):
    u = User()
    u.username = username
    u.set_password(password)
    u.admin = False
    db.session.add(u)
    db.session.commit()
    return u.id


def get_users():
    return User.query.order_by(User.username).all()


def delete_user(username):
    u = User.query.filter_by(username=username).first()
    db.session.delete(u)
    db.session.commit()


def update_reading_list_order(user, ordering):
    print ordering
    for r in ReadingList.query.filter_by(user_id=user.id).all():
        r.position = ordering[unicode(r.book_id)]

    db.session.commit()


def add_to_reading_list(user, book_id):
    r = ReadingList()
    r.user_id = user.id
    r.book_id = book_id
    r.position = 999

    try:
        db.session.add(r)
        db.session.commit()
    except IntegrityError:
        pass


def is_book_in_reading_list(book_id):
    return ReadingList.query.filter_by(user_id=current_user.id, book_id=book_id).first()


def remove_from_reading_list(user, book_id):
    r = ReadingList.query.filter_by(user_id=user.id, book_id=book_id).first()
    db.session.delete(r)
    db.session.commit()


def generate_genre_tree_select_options(selected=None, value_id=False):
    output = ""

    for parent in get_taxonomy_terms_without_parent('genre'):
        output += _recurse_select_level(parent, selected=selected, value_id=value_id)

    return output


def _recurse_select_level(parent, depth=0, selected=None, value_id=False):
    name = ("&mdash;" * depth) + " " + parent.name
    value = parent.id if value_id else parent.name

    selected_string = """ selected="selected" """ if selected == parent.name else ""

    output = """<option value="%s"%s>%s</option>""" % (value, selected_string, name)

    if parent.children:
        for child in parent.children:
            output += _recurse_select_level(child, depth=depth + 1, selected=selected, value_id=value_id)

    return output


def generate_genre_tree_list():
    output = ""

    for parent in get_taxonomy_terms_without_parent('genre'):
        output += _recurse_list_level(parent)

    return output


def _recurse_list_level(parent):
    output = "<li>"
    output += """<a href="#" data-tax-id="{}" data-tax-slug="{}"
                             data-tax-name="{}" data-tax-type="{}"
                             data-tax-parent="{}">{}</a>""".format(
        parent.id, parent.slug, parent.name, parent.type, parent.parent_id, parent.name)

    output += """ <span class="tax-count">{}</span>""".format(len(parent.books))

    if parent.children:
        output = output + "<ul>"
        for child in parent.children:
            output = output + _recurse_list_level(child)

        output = output + "</ul>"

    output = output + "</li>"
    return output


def authenticate(username, password):
    hashed_pass = hashlib.sha1(password).hexdigest()
    user = db.session.query(User).filter(User.username==username).first()
    if user and user.password == hashed_pass:
        return user

    return None
