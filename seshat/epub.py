import zipfile
import os.path
import mimetypes
from lxml import etree


ns = {
    'n': 'urn:oasis:names:tc:opendocument:xmlns:container',
    'pkg': 'http://www.idpf.org/2007/opf',
    'dc': 'http://purl.org/dc/elements/1.1/',
    'opf': 'http://www.idpf.org/2007/opf'
}


def write_epub_meta(epub_file, title, author, cover=None, subjects=[], series=None, series_seq=None):
    metadata = read_epub_metadata_from_file(epub_file)
    p = metadata.xpath('/pkg:package/pkg:metadata', namespaces=ns)[0]

    cover_to_copy = None

    if series:
        prepend_title = series
        if series_seq:
            prepend_title = "%s %d - " % (prepend_title, series_seq)

        title = prepend_title + title

    elem_title = p.xpath('dc:title', namespaces=ns)
    elem_title[0].text = title

    elem_creator = p.xpath('dc:creator', namespaces=ns)
    elem_creator[0].text = author
    elem_creator[0].attrib["{%s}file-as" % ns['opf']] = author

    # remove existing subjects
    elem_subject = p.xpath('dc:subject', namespaces=ns)
    if elem_subject:
        for s in elem_subject:
            s.getparent().remove(s)

    # add new subjects
    if subjects:
        for subject in subjects:
            elem = etree.Element("{%s}subject" % ns['dc'])
            elem.text = subject
            p.insert(-1, elem)

    # remove existing cover
    elem_cover = p.xpath("pkg:meta[@name='cover']", namespaces=ns)
    if elem_cover:
        for elem in elem_cover:
            elem.getparent().remove(elem)

    if cover:
        # add meta cover
        elem = etree.Element("meta", name='cover', content='cover')
        p.insert(-1, elem)

        # find item id="cover"
        manifest = metadata.xpath('/pkg:package/pkg:manifest', namespaces=ns)[0]
        elem_manifest_cover = manifest.xpath("pkg:item[@id='cover']", namespaces=ns)
        # remove old cover
        if elem_manifest_cover:
            elem_manifest_cover[0].getparent().remove(elem_manifest_cover[0])

        # add new cover element
        new_cover_elem = etree.Element("item", id="cover")
        cover_name, cover_ext = os.path.splitext(cover)
        new_cover_elem.attrib['href'] = "cover%s" % cover_ext
        cover_mimetype, cover_encoding = mimetypes.guess_type(cover)
        new_cover_elem.attrib['media-type'] = cover_mimetype
        manifest.insert(-1, new_cover_elem)

        # note cover to copy to zip file
        cover_to_copy = new_cover_elem.attrib['href']

    new_manifest = etree.tostring(metadata)

    cfname = get_epub_manifest_file(epub_file)
    zip = zipfile.ZipFile(epub_file, 'a')
    zip.writestr(cfname, new_manifest)
    if cover_to_copy:
        zip.write(cover, cover_to_copy)


def read_epub_meta(epub_file):
    metadata = read_epub_metadata_from_file(epub_file)
    p = metadata.xpath('/pkg:package/pkg:metadata', namespaces=ns)[0]

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


def read_epub_metadata_from_file(epub_file):
    # http://stackoverflow.com/questions/3114786/python-library-to-extract-epub-information
    cfname = get_epub_manifest_file(epub_file)
    # grab the metadata block from the contents metafile
    zip = zipfile.ZipFile(epub_file)# 
    cf = zip.read(cfname)
    tree = etree.fromstring(cf)

    return tree
