import re, math
from jinja2 import evalcontextfilter, Markup, escape


@evalcontextfilter
def nl2br(eval_ctx, value):
    _paragraph_re = re.compile(r'(?:\r\n|\r|\n){2,}')
    result = u'\n\n'.join(u'<p>%s</p>' % p.replace('\n', '<br>\n') \
        for p in _paragraph_re.split(escape(value)))
    if eval_ctx.autoescape:
        result = Markup(result)
    return result


def none2blank(value):
    if value is None:
        return ""
    else:
        return value


def rough_format(value):
    n = int(value)

    if n < 1000:
        return str(value)
    elif n < 1000000: # < 1 million
        return str(int(math.ceil(value / 1000))) + 'k'
    else: # > 1 million
        return str(int(math.ceil(value / 1000000))) + 'm'
