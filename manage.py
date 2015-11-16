#!/usr/bin/env python
import uuid
import os
from lxml import etree
from flask.ext.script import Manager
from flask.ext.alembic import ManageMigrations
import html2text
from literable import app, model, epub, book_upload_set


manager = Manager(app)
manager.add_command("migrate", ManageMigrations())


@manager.command
def debug():
    """ Run the server in debug mode"""
    app.run('0.0.0.0', debug=True, threaded=True)


@manager.command
def write_meta():
    """Write meta to ebook files"""
    for book in model.get_all_books():
        print "Writing meta for %s" % book.title
        book.write_meta()


@manager.command
def read_epub_meta(book_path):
    """Read metadata for an ePub file"""
    e = epub.Epub(book_path)
    print e.metadata
    print e.cover
    e.extract_cover('/tmp/{}'.format(e.cover))


@manager.command
def add_user(username, password):
    id = model.add_user(username, password)
    print "User added with ID {0}".format(id)


@manager.command
def count_words():
    books = model.get_all_books()

    for book in books:
        if not book.word_count:
            book.update_word_count()


@manager.command
def list_users():
    for user in model.get_users():
        print user


@manager.command
def delete_user(username):
    model.delete_user(username)
    print "User deleted"

@manager.command
def batch_import(directory):
    batch = str(uuid.uuid4())
    count = 0
    success = 0
    print "Importing batch " + batch
    for root, subdirs, files in os.walk(directory):
        try:
            book_file = None
            metadata = {}
            cover_file = None

            for filename in files:
                file_path = os.path.join(root, filename)
                if filename == "metadata.opf":
                    with open(file_path) as mf:
                        e = etree.fromstring(mf.read()).xpath('/pkg:package/pkg:metadata', namespaces={
                            'n': 'urn:oasis:names:tc:opendocument:xmlns:container',
                            'pkg': 'http://www.idpf.org/2007/opf',
                            'dc': 'http://purl.org/dc/elements/1.1/',
                            'opf': 'http://www.idpf.org/2007/opf'
                        })[0]
                        vals = epub.read_opf(e)
                        if 'description' in vals:
                            h = html2text.HTML2Text()
                            vals['description'] = h.handle(vals['description'])

                        metadata = vals
                elif "epub" in filename or "pdf" in filename:
                    book_file = filename
                elif filename == "cover.jpg":
                    cover_file = filename

            if not book_file:
                continue

            count += 1

            if not metadata or not cover_file:
                print "WARN: No metadata or no cover file found for book " + book_file

            model.add_book_bulk(batch, root, book_file, cover_file, metadata)
        except Exception as e:
            print "Exception importing files from " + root
            print e
        else:
            success += 1

    print "Finished batch. Imported " + str(success) + " of " + str(count) + " books."


@manager.command
def batch_remove(batch_id):
    successful, total = model.remove_books_from_batch(batch_id)
    print "Removed " + str(successful) + " of " + str(total) + " books in batch."

if __name__ == "__main__":
    manager.run()
