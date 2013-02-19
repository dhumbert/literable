import zipfile
from lxml import etree
from seshat import model, book_upload_set, cover_upload_set


ns = {
    'n': 'urn:oasis:names:tc:opendocument:xmlns:container',
    'pkg': 'http://www.idpf.org/2007/opf',
    'dc': 'http://purl.org/dc/elements/1.1/'
}


def write_all_meta():
    books = model.get_all_books()

    for book in books:
        if book.filename and book.get_format() == 'epub':
            epub_file = book_upload_set.path(book.filename)

            if book.cover:
                cover = cover_upload_set.path(book.cover)
            else:
                cover = None

            if book.series:
                series = book.series.title
            else:
                series = None
            #print read_epub_meta(epub_file)['subject']

            if book.genre:
                genre = [book.genre.name]
            else:
                genre = []

            subjects = genre

            write_epub_meta(epub_file, book.title, book.author.name,
                cover=cover, series=series,
                series_seq=book.series_seq,
                subjects=subjects)


def write_epub_meta(epub_file, title, author, cover=None, subjects=[], series=None, series_seq=None):
    manifest = read_epub_manifest(epub_file)
    p = manifest.xpath('/pkg:package/pkg:metadata', namespaces=ns)[0]

    if series:
        prepend_title = series
        if series_seq:
            prepend_title = "%s %d - " % (prepend_title, series_seq)

        title = prepend_title + title

    elem_title = p.xpath('dc:title', namespaces=ns)
    elem_title[0].text = title

    elem_creator = p.xpath('dc:creator', namespaces=ns)
    elem_creator[0].text = author

    elem_subject = p.xpath('dc:subject', namespaces=ns)
    if elem_subject:
        for s in elem_subject:
            s.getparent().remove(s)

    if subjects:
        for subject in subjects:
            pass
            #elem = etree.Element(etree.QName(ns['dc'], 'subject'), subject, nsmap=ns)
            #p.insert(-1, elem)

    new_manifest = etree.tostring(manifest)
    print new_manifest
    cfname = get_epub_manifest_file(epub_file)
    zip = zipfile.ZipFile(epub_file, 'a')
    zip.writestr(cfname, new_manifest)


def read_epub_meta(epub_file):
    manifest = read_epub_manifest(epub_file)
    p = manifest.xpath('/pkg:package/pkg:metadata', namespaces=ns)[0]

    # repackage the data
    res = {}
    for s in ['title', 'creator', 'description', 'subject']:
        item = p.xpath('dc:%s/text()' % (s), namespaces=ns)
        if item:
            if len(item) > 1:
                res[s] = []
                for i in item:
                    res[s].append(i)
            else:
                res[s] = item[0]

    return res


def get_epub_manifest_file(epub_file):
    zip = zipfile.ZipFile(epub_file)
    txt = zip.read('META-INF/container.xml')
    tree = etree.fromstring(txt)
    cfname = tree.xpath('n:rootfiles/n:rootfile/@full-path', namespaces=ns)[0]

    return cfname


def read_epub_manifest(epub_file):
    # http://stackoverflow.com/questions/3114786/python-library-to-extract-epub-information
    cfname = get_epub_manifest_file(epub_file)
    # grab the metadata block from the contents metafile
    zip = zipfile.ZipFile(epub_file)# 
    cf = zip.read(cfname)
    tree = etree.fromstring(cf)

    return tree
