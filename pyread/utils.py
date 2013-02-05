import re
import Image
from pyread import cover_upload_set


def slugify(text, delim=u'-'):
    """Generates an ASCII-only slug."""
    _punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')
    result = []
    for word in _punct_re.split(text.lower()):
        if word:
            result.append(word)
    return unicode(delim.join(result))


def create_thumbnail(file):
    image = Image.open(cover_upload_set.path(file))
    image.thumbnail((70, 100), Image.ANTIALIAS)
    new_filename = "thumb-%s" % file
    image.save(cover_upload_set.path(new_filename))
