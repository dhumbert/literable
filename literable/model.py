from datetime import datetime
import hashlib
import re
import shutil
import os
import os.path
from flask import flash
from flask.ext.login import current_user
from sqlalchemy import or_, and_, desc, asc
from sqlalchemy.sql.expression import func
from PIL import Image
from literable import db, app, book_staging_upload_set, tmp_cover_upload_set, cover_upload_set, book_upload_set, epub
from literable.orm import Book, User, ReadingList, Taxonomy, Rating, ReadingListBookAssociation


def _get_page(page):
    if page is None:
        page = 1
    else:
        page = int(page)
    return page


def _privilege_filter():
    return or_(Book.user_id == current_user.id, Book.public)


def user_can_modify_book(book, user):
    return user.can_modify_book(book)


def user_can_download_book(book, user):
    return book.public or user_can_modify_book(book, user)


def get_books(page):
    page = max(1, _get_page(page))
    return Book.query.order_by(Book.title_sort).paginate(page, per_page=app.config['BOOKS_PER_PAGE'])


def get_random_books(n):
    f = or_() if current_user.admin else _privilege_filter()
    f = and_(f, Book.archived == False)
    return Book.query.filter(f).order_by(func.random()).limit(n).all()


def get_archived_books(page):
    page = max(1, _get_page(page))
    f = or_() if current_user.admin else _privilege_filter()
    f = and_(f, Book.archived == True)
    return Book.query.filter(f).order_by(Book.title_sort).paginate(page, per_page=app.config['BOOKS_PER_PAGE'])


def get_all_books():
    return Book.query.order_by(Book.title_sort).all()


def get_book(id):
    if id is None:
        return Book()  # blank book object
    else:
        return Book.query.get_or_404(id)


def get_book_by_identifier(id_type, identifer):
    return Book.query.filter_by(**{'id_' + id_type: identifer}).first()


def _get_sort_objs(sort, sort_dir):
    sort_dir = asc if sort_dir == 'asc' else desc

    sort_criterion = Book.created_at
    if sort == 'title':
        sort_criterion = Book.title_sort
    elif sort == 'word_count':
        sort_criterion = Book.word_count

    return sort_criterion, sort_dir


def get_recent_books(page, sort, sort_dir):
    page = max(1, _get_page(page))

    f = or_() if current_user.admin else _privilege_filter()

    f = and_(f, Book.archived == False)

    sort_criterion, sort_dir = _get_sort_objs(sort, sort_dir)

    return Book.query.filter(f).order_by(sort_dir(sort_criterion)).paginate(page, per_page=app.config['BOOKS_PER_PAGE'])


def search_books(q):

    f = or_(
        Book.title.ilike('%'+q+'%'),
        Book.description.ilike('%'+q+'%'),
        Taxonomy.name.ilike('%'+q+'%'),
    )

    if not current_user.admin:
        f = and_(f, _privilege_filter())

    query = Book.query.join(Book.taxonomies).filter(f)

    scores = {}

    # super-naive scoring method
    for result in query.all():
        score = 0
        lower_title = result.title.lower().replace("'s", "")
        if q.lower() in lower_title.split(): # whole words
            score += 100 * len(filter(lambda x: q.lower() == x.lower(), unicode(lower_title).split()))
        elif q.lower() in lower_title:
            score += 75

        for field in [result.description.replace("'s", "")] + result.taxonomies:
            score += 4 * len(filter(lambda x: q.lower() == x.lower(), unicode(field).split()))  # rank whole-word higher
            score += len(filter(lambda x: q.lower() == x.lower(), unicode(field)))


        scores[result.id] = (score, result,)

    num_results = 25
    return map(lambda y: y[1][1], sorted(scores.iteritems(), key=lambda x: x[1][0], reverse=True))[0:num_results]


def get_incomplete_books():
    books = {
        'without a cover': [],
        'without a description': [],
        'without a file': [],
        'without an author': [],
        'without a publisher': [],
        'without a word count': [],
        'with word count < 1000': [],
        'without a calibre id': [],
        'without an isbn': [],
        'that are duplicate': []
    }

    book_titles = set()

    for book in get_all_books():
        if book.title in book_titles:
            books['that are duplicate'].append(book)
        else:
            book_titles.add(book.title)

        if not book.authors:
            books['without an author'].append(book)
        if not book.cover:
            books['without a cover'].append(book)
        if not book.filename:
            books['without a file'].append(book)
        if not book.description:
            books['without a description'].append(book)
        if not book.publishers:
            books['without a publisher'].append(book)
        if not book.word_count:
            books['without a word count'].append(book)
        if book.word_count and book.word_count < 1000:
            books['with word count < 1000'].append(book)
        if not book.id_calibre:
            books['without a calibre id'].append(book)
        if not book.id_isbn:
            books['without an isbn'].append(book)

    return books


def get_book_covers():
    covers = []
    for book in get_all_books():
        if book.cover:
            f = cover_upload_set.path(book.cover)
            if os.path.exists(f):
                filesize = os.stat(f).st_size
                i = Image.open(f)
                covers.append({
                    'book': book,
                    'dimensions': '{0}x{1}'.format(*i.size),
                    'size': filesize / 1000
                })

    return sorted(covers, key=lambda x: x['size'], reverse=True)


def get_taxonomy_books(tax_type, tax_slug, page=None, sort='created', sort_dir='desc'):
    page = max(1, _get_page(page))

    f = or_() if current_user.admin else _privilege_filter()
    f = and_(f, Book.archived == False)
    tax = Taxonomy.query.filter_by(type=tax_type, slug=tax_slug).first_or_404()
    q = Book.query.filter(and_(Book.taxonomies.any(Taxonomy.id == tax.id), f))

    if tax_type == 'series':
        q = q.order_by(Book.series_seq, Book.title_sort)
    else:
        sort_criterion, sort_dir = _get_sort_objs(sort, sort_dir)
        q = q.order_by(sort_dir(sort_criterion))

    books = q.paginate(page, per_page=app.config['BOOKS_PER_PAGE'])
    books = None if len(books.items) == 0 else books

    return (books, tax)


def get_taxonomy_terms(ttype):
    return Taxonomy.query.filter_by(type=ttype).order_by(Taxonomy.name)


def get_taxonomy_terms_and_counts(ttype, order=None):
    return Taxonomy.get_grouped_counts(ttype, order)


def get_taxonomy_types():
    return Taxonomy.get_types()


def get_taxonomy_term(ttype, term):
    return Taxonomy.query.filter_by(type=ttype, name=term).first()


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
    book.title_sort = form['title_sort']
    book.description = form['description']
    book.series_seq = int(form['series_seq']) if form['series_seq'] else None
    book.public = True if form['privacy'] == 'public' else False
    book.user = current_user
    book.created_at = datetime.now()
    book.archived = False
    book.reading_time_formatted = form['reading_time']

    book.id_isbn = form['id_isbn']
    book.id_calibre = form['id_calibre']

    book.update_taxonomies({
        'author':  [(form['author'], form['author_sort'])],
        'publisher': [form['publisher']],
        'series': [form['series']],
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

    book.update_word_count()

    return True


def add_book_bulk(batch, root, book_file, cover_file, metadata):
    if 'title' not in metadata or not metadata['title'].strip():
        raise ValueError("Title must not be blank: " + book_file)

    ids = {'isbn': metadata.get('id_isbn'),
           'calibre': metadata.get('id_calibre'),
           'amazon': metadata.get('id_amazon'),
           'google': metadata.get('id_google')}

    for id_type, identifer in ids.iteritems():
        if identifer:
            if get_book_by_identifier(id_type, identifer):
                raise RuntimeError("There is already a book with identifier [" + id_type + ": " + identifer + "]!")

    book = Book()
    book.batch = batch
    book.title = metadata['title']
    book.title_sort = metadata['title_sort'] if 'title_sort' in metadata else metadata['title']
    book.description = metadata['description'] if 'description' in metadata else None
    book.series_seq = int(metadata['series_index']) if 'series_index' in metadata else None
    book.public = True
    book.user = get_user('devin')
    book.created_at = datetime.now()

    book.id_isbn = ids['isbn']
    book.id_amazon = ids['amazon']
    book.id_google = ids['google']
    book.id_calibre = ids['calibre']

    taxonomies = {}

    if 'publisher' in metadata:
        taxonomies['publisher'] = [metadata['publisher']]
    if 'series' in metadata:
        taxonomies['series'] = [metadata['series']]

    if 'creator' in metadata and 'creator_sort' in metadata:
        if isinstance(metadata['creator'], list):
            taxonomies['author'] = []
            for i, c in enumerate(metadata['creator']):
                taxonomies['author'].append((c, metadata['creator_sort'][i]))
        else:
            taxonomies['author'] = [ (metadata['creator'], metadata['creator_sort'])]
    elif 'creator' in metadata:
        if isinstance(metadata['creator'], list):
            taxonomies['author'] = []
            for i, c in enumerate(metadata['creator']):
                taxonomies['author'].append((c, c))
        else:
            taxonomies['author'] = [ (metadata['creator'], metadata['creator'])]

    if 'subject' in metadata:
        tags = []
        if not isinstance(metadata['subject'], list):
            metadata['subject'] = [metadata['subject']]

        for subject in metadata['subject']:
            tags.append(subject.lower())

        if len(tags) > 0:
            taxonomies['tag'] = tags

    book.update_taxonomies(taxonomies)

    cover_dest_path = cover_upload_set.config.destination
    new_cover_file = re.sub('[^0-9a-zA-Z\._\-]+', '', cover_file.replace(" ", "_"))

    if os.path.exists(os.path.join(cover_dest_path, new_cover_file)):
        new_cover_file = cover_upload_set.resolve_conflict(cover_dest_path, new_cover_file)
        
    shutil.copy(os.path.join(root, cover_file), cover_upload_set.path(new_cover_file))
    
    book_dest_path = book_upload_set.config.destination
    new_book_file = re.sub('[^0-9a-zA-Z\._\-]+', '', book_file.replace(" ", "_"))

    if os.path.exists(os.path.join(book_dest_path, new_book_file)):
        new_book_file = book_upload_set.resolve_conflict(book_dest_path, new_book_file)
        
    shutil.copy(os.path.join(root, book_file), book_upload_set.path(new_book_file))

    book.cover = new_cover_file
    book.filename = new_book_file

    db.session.add(book)

    if 'rating' in metadata and metadata['rating'] > 0:
        rating = Rating()
        rating.user_id = book.user.id
        rating.book_id = book.id
        rating.rating = metadata['rating']
        db.session.add(rating)

    db.session.commit()

    if app.config['WRITE_META_ON_SAVE']:
       book.write_meta()

    book.update_word_count()

    return True


def edit_book(id, form, files):
    book = get_book(id)
    if book:
        if not user_can_modify_book(book, current_user):
            return False

        book.title = form['title']
        book.title_sort = form['title_sort']
        book.description = form['description']
        book.series_seq = int(form['series_seq']) if form['series_seq'] else None
        book.public = True if form['privacy'] == 'public' else False

        book.id_isbn = form['id_isbn']
        book.id_calibre = form['id_calibre']
        book.reading_time_formatted = form['reading_time']

        book.update_taxonomies({
            'author': [(form['author'], form['author_sort'])],
            'publisher': [form['publisher']],
            'series': [form['series']],
            'tag': form['tags'].split(','),
        })

        if 'meta-cover' in form and form['meta-cover']:
            book.move_cover_from_tmp(form['meta-cover'])
        elif 'cover' in files and files['cover']:
            book.attempt_to_update_cover(files['cover'])

        if 'file' in form and form['file']:
            book.move_file_from_staging(form['file'])
            book.update_word_count()

        db.session.commit()

        if app.config['WRITE_META_ON_SAVE']:
            book.write_meta()

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
                if 'creator' in meta:
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


def rate_book(book_id, score):
    rating = Rating.query.filter_by(book_id=book_id, user_id=current_user.id).first()
    if rating:
        rating.rating = score
    else:
        rating = Rating()
        rating.user_id = current_user.id
        rating.book_id = book_id
        rating.rating = score
        db.session.add(rating)

    db.session.commit()


def archive_book(id):
    book = get_book(id)

    if not user_can_modify_book(book, current_user):
        flash('You cannot archive a book you do not own', 'error')
        return False

    book.archived = True
    db.session.commit()


def restore_book(id):
    book = get_book(id)

    if not user_can_modify_book(book, current_user):
        flash('You cannot restore a book you do not own', 'error')
        return False

    book.archived = False
    db.session.commit()


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


def remove_books_from_batch(batch_id):
    total = 0
    successful = 0
    for book in Book.query.filter_by(batch=batch_id).all():
        total += 1
        try:
            book.remove_file()
        except Exception as e:
            print "Unable to delete file!"
            print e

        try:
            book.remove_cover()
        except Exception as e:
            print "Unable to delete cover!"
            print e

        try:
            db.session.delete(book)
            successful += 1

        except Exception as e:
            print "Unable to delete book! " + book
            print e

    db.session.commit()

    return successful, total


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
    new = False
    if 'id' in data and data['id']:
        tax = Taxonomy.query.get(data['id'])
    else:
        new = True
        tax = Taxonomy()
        tax.type = data['type']

    if not tax:
        return False

    tax.name = data['name']
    tax.name_sort = data['name']
    tax.slug = tax.generate_slug()

    if 'parent' in data and data['parent']:
        tax.parent_id = int(data['parent'])
    else:
        tax.parent_id = None

    if new:
        db.session.add(tax)

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


def get_user(username):
    return User.query.filter_by(username=username).first()


def delete_user(username):
    u = User.query.filter_by(username=username).first()
    db.session.delete(u)
    db.session.commit()


def delete_reading_list(list_id):
    rlist = ReadingList.query.filter_by(id=list_id).first()
    if rlist:
        if rlist.user_id == current_user.id:
            db.session.delete(rlist)
            db.session.commit()
        else:
            raise
    else:
        raise


def new_reading_list(name):
    rlist = ReadingList()
    rlist.user_id = current_user.id
    rlist.name = name
    rlist.slug = rlist.generate_slug()

    db.session.add(rlist)
    db.session.commit()


def update_reading_list_order(list_id, ordering):
    rlist = ReadingList.query.filter_by(id=list_id).first()
    for rbook in rlist._books:
        rbook.position = ordering[unicode(rbook.book_id)]

    db.session.commit()


def add_to_reading_list(list_id, book_id):
    r = ReadingListBookAssociation()
    r.book_id = book_id
    r.reading_list_id = list_id
    r.position = 999

    db.session.add(r)
    db.session.commit()


def remove_from_reading_list(list_id, book_id):
    r = ReadingListBookAssociation.query.filter_by(reading_list_id=list_id, book_id=book_id).first()
    db.session.delete(r)
    db.session.commit()


def generate_hierarchical_taxonomy_list(tax, selected=None, css_class=None):
    output = '<ul'
    output += ' class="{}"'.format(css_class) if css_class else ''
    output += ' data-name="hierarchical_tax_{}"'.format(tax)
    output += '>'

    for parent in get_taxonomy_terms_without_parent(tax):
        output += _recurse_hierarchical_list_level(parent, selected=selected)

    return output + "</ul>"


def _recurse_hierarchical_list_level(parent, depth=0, selected=None):
    output = '<li data-value="{}"'.format(parent.id)
    if selected and parent.id in selected:
        output += ' data-checked="1"'
    output += '>'

    output += parent.name

    if parent.children:
        output += "<ul>"
        for child in parent.children:
            output += _recurse_hierarchical_list_level(child, depth=depth+1, selected=selected)
        output += "</ul>"

    return output + "</li>"


def authenticate(username, password):
    hashed_pass = hashlib.sha1(password).hexdigest()
    user = db.session.query(User).filter(User.username==username).first()
    if user and user.password == hashed_pass:
        return user

    return None


def save_updated_books(books):
    db.session.commit()