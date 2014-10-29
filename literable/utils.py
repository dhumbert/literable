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


def authorify(name):
    """
    Convert Devin Humbert to Humbert, Devin
    """
    final = name

    name_split = name.split(' ')
    if len(name_split) > 1:
        final = u"{}, {}".format(name_split[-1], " ".join(name_split[0:-1]))

    return final