import zipfile
import tempfile
import shutil
import os.path
import uuid
import mimetypes
from lxml import etree


ns = {
    'n': 'urn:oasis:names:tc:opendocument:xmlns:container',
    'pkg': 'http://www.idpf.org/2007/opf',
    'dc': 'http://purl.org/dc/elements/1.1/',
    'opf': 'http://www.idpf.org/2007/opf'
}


# todo move the helper funcs at bottom to this class
class Epub:
    def __init__(self, epub_file):
        self.epub_file = epub_file

    @property
    def manifest_filename(self):
        """Get the filename of the manifest file"""
        pass

    @property
    def manifest(self):
        """Get the contents of the manifest file as XML"""
        pass


class EpubMetadataCreator:
    def __init__(self, epub_file):
        self.epub_file = epub_file
        self.meta_element = etree.Element("metadata", nsmap=ns)
        self.title = None
        self.author = None
        self.description = None
        self.subjects = None

    def set_title(self, title, series=None, series_seq=None):
        if series:
            prepend_title = series
            if series_seq:
                prepend_title = "%s %d - " % (prepend_title, series_seq)

            self.title = prepend_title + title

    def build(self):
        self._build_overwritable_elements()
        self._build_nonoverwritable_elements()
        self._build_cover()

    def _build_overwritable_elements(self):
        simple_overwritable_elements = {
            'title': self.title,
            'creator': self.author,
            'description': self.description
        }

        for element in simple_overwritable_elements:
            e = etree.Element("{%s}%s" % (ns['dc'], element))
            e.text = simple_overwritable_elements[element]
            self.meta_element.insert(-1, e)

    def _build_nonoverwritable_elements(self):
        # some metadata we should leave if it exists
        # but if it doesn't, add our own
        existing_metadata = read_epub_meta(self.epub_file)

        non_overwritable_elements = {
            'identifier': uuid.uuid4().hex,
            'language': 'en-US'
        }

        for noe in non_overwritable_elements:
            e = etree.Element("{%s}%s" % (ns['dc'], noe))
            if existing_metadata and noe in existing_metadata:
                e.text = existing_metadata[noe]
            else:
                e.text = non_overwritable_elements[noe]

            self.meta_element.insert(-1, e)

    def _build_cover(self):
        if self.cover:
            e = etree.Element("meta", name='cover', content='cover')
            self.meta_element.insert(-1, e)

    def __str__(self):
        self.build()
        return etree.tostring(self.meta_element, pretty_print=True)


def write_epub_meta(epub_file, title, author, description=None, cover=None, subjects=[], series=None, series_seq=None):
    creator = EpubMetadataCreator(epub_file)

    creator.set_title(title, series, series_seq)
    creator.author = author
    creator.description = description
    creator.cover = cover
    creator.subjects = subjects

    manifest = replace_metadata_element(epub_file, str(creator))
    cfname = get_epub_manifest_file(epub_file)

    # remove old manifest file
    remove_from_zip(epub_file, cfname)

    zip = zipfile.ZipFile(epub_file, 'a')
    zip.writestr(cfname, etree.tostring(manifest, pretty_print=True))


def replace_metadata_element(epub_file, metadata_element_string):
    new_metadata_element = etree.fromstring(metadata_element_string)
    manifest = read_epub_manifest_from_file(epub_file)
    old_metadata_element = get_epub_metadata_element(manifest)

    if old_metadata_element is not None:
        manifest.remove(old_metadata_element)

    manifest.insert(0, new_metadata_element)

    return manifest


def remove_from_zip(zipfname, *filenames):
    tempdir = tempfile.mkdtemp()
    try:
        tempname = os.path.join(tempdir, 'new.zip')
        with zipfile.ZipFile(zipfname, 'r') as zipread:
            with zipfile.ZipFile(tempname, 'w') as zipwrite:
                for item in zipread.infolist():
                    if item.filename not in filenames:
                        data = zipread.read(item.filename)
                        zipwrite.writestr(item, data)
        shutil.move(tempname, zipfname)
    finally:
        shutil.rmtree(tempdir)


# todo: delete this function when done tearing stuff out of it
def _xwrite_epub_meta(epub_file, title, author, description=None, cover=None, subjects=[], series=None, series_seq=None):
    metadata = read_epub_manifest_from_file(epub_file)
    p = metadata.xpath('/pkg:package/pkg:metadata', namespaces=ns)[0]

    cover_to_copy = None

    if series:
        prepend_title = series
        if series_seq:
            prepend_title = "%s %d - " % (prepend_title, series_seq)

        title = prepend_title + title

    elem_title = p.xpath('dc:title', namespaces=ns)
    elem_title[0].text = title

    elem_description = p.xpath('dc:description', namespaces=ns)
    if elem_description:
        elem_description[0].text = description
    else:
        elem = etree.Element("{%s}description" % ns['dc'])
        elem.text = description
        p.insert(-1, elem)

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
    print new_manifest
    cfname = get_epub_manifest_file(epub_file)
    zip = zipfile.ZipFile(epub_file, 'a')
    zip.writestr(cfname, new_manifest)
    if cover_to_copy:
        zip.write(cover, cover_to_copy)


def read_epub_meta(epub_file):
    metadata = read_epub_manifest_from_file(epub_file)
    if metadata is not None:
        p = metadata.xpath('/pkg:package/pkg:metadata', namespaces=ns)

        if len(p) > 0:
            p = p[0]
            # repackage the data
            res = {}
            for s in ['title', 'creator', 'description', 'subject', 'identifier', 'language']:
                item = p.xpath('dc:%s/text()' % (s), namespaces=ns)
                if item:
                    if len(item) > 1:
                        res[s] = []
                        for i in item:
                            res[s].append(i)
                    else:
                        res[s] = item[0]

            return res
        else:
            return None


def get_epub_manifest_file(epub_file):
    zip = zipfile.ZipFile(epub_file)
    txt = zip.read('META-INF/container.xml')
    zip.close()
    tree = etree.fromstring(txt)

    cfname = tree.xpath('n:rootfiles/n:rootfile/@full-path', namespaces=ns)[0]

    return cfname


def read_epub_manifest_from_file(epub_file):
    # http://stackoverflow.com/questions/3114786/python-library-to-extract-epub-information
    cfname = get_epub_manifest_file(epub_file)

    # grab the metadata block from the contents metafile
    zip = zipfile.ZipFile(epub_file)
    try:
        cf = zip.read(cfname)
        tree = etree.fromstring(cf)
    except KeyError:
        tree = None
    finally:
        zip.close()

    return tree


def get_epub_metadata_element(manifest):
    if manifest is not None:
        metadata = manifest.xpath('/pkg:package/pkg:metadata', namespaces=ns)
        if metadata is not None:
            return metadata[0]
        else:
            return None
