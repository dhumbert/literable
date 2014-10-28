import zipfile
import tempfile
import shutil
import os.path
import uuid
import mimetypes
from lxml import etree


# help from http://stackoverflow.com/questions/3114786/python-library-to-extract-epub-information

ns = {
    'n': 'urn:oasis:names:tc:opendocument:xmlns:container',
    'pkg': 'http://www.idpf.org/2007/opf',
    'dc': 'http://purl.org/dc/elements/1.1/',
    'opf': 'http://www.idpf.org/2007/opf'
}


class Epub:
    """Reads and writes metadata for an epub file"""

    def __init__(self, epub_file):
        self.epub_file = epub_file
        self.cover = None
        self._read()

    def replace_metadata_element(self, new_element):
        """Replace the metadata element in the manifest with a new one"""
        new_metadata_element = etree.fromstring(str(new_element))
        old_metadata_element = self.metadata_element

        if old_metadata_element is not None:
            old_metadata_element.getparent().remove(old_metadata_element)

        self.manifest.insert(0, new_metadata_element)

        return self.manifest

    def save(self):
        """Save the epub file"""
        self._remove_deprecated_elements()
        self._process_cover()

        # remove old manifest file
        remove_from_zip(self.epub_file, self.manifest_filename)
        content = etree.tostring(self.manifest, pretty_print=True)
        self._write_string_to_epub(self.manifest_filename, content)

    def _read_from_epub(self, filename):
        """Read a file from the epub archive"""
        zip = zipfile.ZipFile(self.epub_file)
        try:
            content = zip.read(filename)
        except KeyError:
            content = None
        finally:
            zip.close()

        return content

    def _write_string_to_epub(self, filename, content):
        """Write a string to a file in the epub archive"""
        zip = zipfile.ZipFile(self.epub_file, 'a')
        zip.writestr(filename, content)
        zip.close()

    def _write_file_to_epub(self, orig_file, dest_file):
        """Write a file to the epub archive"""
        zip = zipfile.ZipFile(self.epub_file, 'a')
        zip.write(orig_file, dest_file)
        zip.close()

    def _read(self):
        """Read all the stuff we need from the epub"""
        self.manifest_filename = self._read_manifest_filename()
        self.manifest = self._read_manifest()
        self.metadata_element = self._read_metadata_element()
        self.metadata = self._read_metadata()
        self.cover = self._read_cover()

    def _read_manifest_filename(self):
        """Read filename of the manifest file"""
        content = self._read_from_epub('META-INF/container.xml')
        tree = etree.fromstring(content)

        cfname = tree.xpath('n:rootfiles/n:rootfile/@full-path', namespaces=ns)[0]

        return cfname

    def _read_manifest(self):
        """Read contents of the manifest file as XML"""
        content = self._read_from_epub(self.manifest_filename)
        if content is not None:
            return etree.fromstring(content)

    def _read_metadata(self):
        """Read epub metadata as a list"""
        res = {}
        metadata = self.metadata_element
        if metadata is not None:
            # repackage the data
            for s in ['title', 'creator', 'description', 'subject', 'identifier', 'language', 'publisher']:
                item = metadata.xpath('dc:%s/text()' % (s), namespaces=ns)
                if item:
                    if len(item) > 1:
                        res[s] = []
                        for i in item:
                            res[s].append(i)
                    else:
                        res[s] = item[0]

        return res

    def _read_metadata_element(self):
        """Read metadata XML element from manifest file"""
        if self.manifest is not None:
            metadata = self.manifest.xpath('/pkg:package/pkg:metadata', namespaces=ns)

            if metadata is not None:
                return metadata[0]

    def _read_cover(self):
        try_ids = ['cover-image', 'coverimagestandard']
        try:
            for try_id in try_ids:

                cover = self.manifest.xpath("pkg:manifest/pkg:item[@id='{}']".format(try_id), namespaces=ns)
                if cover:
                    cover = cover[0]
                    return cover.attrib['href']
        except:
            pass
        return None

    def extract_cover(self, dest):
        if self.cover:
            cover_content = self._read_from_epub(os.path.join('OEBPS', self.cover))

            with open(dest, 'wb') as cover_file:
                cover_file.write(cover_content)

    def _remove_deprecated_elements(self):
        deprecated_elements = ['/pkg:package/pkg:guide']
        for element in deprecated_elements:
            e = self.manifest.xpath(element, namespaces=ns)
            if e is not None and len(e) > 0:
                e[0].getparent().remove(e[0])

    def _process_cover(self):
        if self.cover:
            filename = self._add_cover_to_manifest()
            self._copy_cover_to_epub(filename)

    def _add_cover_to_manifest(self):
        # remove old cover
        elem_manifest_cover = self.manifest.xpath("pkg:item[@id='cover']", namespaces=ns)
        if elem_manifest_cover:
            elem_manifest_cover[0].getparent().remove(elem_manifest_cover[0])

        e = etree.Element("item", id="cover")
        cover_name, cover_ext = os.path.splitext(self.cover)
        e.attrib['href'] = "cover%s" % cover_ext
        e.attrib['properties'] = "cover-image"
        cover_mimetype, cover_encoding = mimetypes.guess_type(self.cover)
        e.attrib['media-type'] = cover_mimetype
        self.manifest.xpath('/pkg:package/pkg:manifest', namespaces=ns)[0].insert(-1, e)
        return e.attrib['href']

    def _copy_cover_to_epub(self, filename):
        path = os.path.dirname(self.manifest_filename)
        filename = os.path.join(path, filename)
        self._write_file_to_epub(self.cover, filename)


class EpubMetadataCreator:
    """Build metadata for an epub"""

    def __init__(self, epub):
        self.epub = epub
        self.meta_element = etree.Element("metadata", nsmap=ns)
        self.title = None
        self.author = None
        self.description = None
        self.subjects = None
        self.cover = None

    def build(self):
        self._build_overwritable_elements()
        self._build_nonoverwritable_elements()
        self._build_subjects()
        self._build_cover()

        self.epub.replace_metadata_element(str(self))

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
        existing_metadata = self.epub.metadata

        non_overwritable_elements = {
            'identifier': uuid.uuid4().hex,
            'language': 'en-US'
        }

        for noe in non_overwritable_elements:
            e = etree.Element("{%s}%s" % (ns['dc'], noe))
            if existing_metadata and noe in existing_metadata:
                e.text = existing_metadata[noe][0]
            else:
                e.text = non_overwritable_elements[noe]

            self.meta_element.insert(-1, e)

    def _build_subjects(self):
        if self.subjects:
            for subject in self.subjects:
                e = etree.Element("{%s}subject" % ns['dc'])
                e.text = subject
                self.meta_element.insert(-1, e)

    def _build_cover(self):
        if self.cover:
            e = etree.Element("meta", name='cover', content='cover')
            self.epub.cover = self.cover

    def __str__(self):
        return etree.tostring(self.meta_element, pretty_print=True)


def write_epub_meta(epub_file, title, author, description=None, cover=None, subjects=[]):
    epub = Epub(epub_file)

    creator = EpubMetadataCreator(epub)
    creator.title = title
    creator.author = author
    creator.description = description
    creator.cover = cover
    creator.subjects = subjects
    creator.build()

    epub.save()


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
