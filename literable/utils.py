import re
import Image
from literable import cover_upload_set


def slugify(text, delim=u'-'):
    """Generates an ASCII-only slug."""
    _punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')
    result = []
    for word in _punct_re.split(text.lower()):
        if word:
            result.append(word)
    return unicode(delim.join(result))
