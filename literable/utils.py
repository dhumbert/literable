import re


def slugify(text, delim=u'-'):
    """Generates an ASCII-only slug."""
    _punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')
    result = []
    for word in _punct_re.split(text.lower()):
        if word:
            result.append(word)
    return unicode(delim.join(result))


def parse_duration_string(duration_string):
    """
    Parses a string like 1w 2d 1h 20m into number of minutes
    :param str duration_string: The string.
    :return: The number of minutes.
    """
    duration = 0
    tokens = duration_string.split(" ")
    cur_token = tokens.pop(0)
    while cur_token:
        if not cur_token[0].isdigit():
            raise SyntaxError("Malformed duration string [" + duration_string + "]")

        pos = 0
        number = ""
        while pos < len(cur_token) and cur_token[pos].isdigit():
            number += cur_token[pos]
            pos += 1

        if pos != len(cur_token) - 1:
            raise SyntaxError("Malformed duration string [" + duration_string + "]. Time unit must be one character")

        time_unit = cur_token[pos]

        if time_unit == "m":
            duration += int(number)
        elif time_unit == "h":
            duration += int(number) * 60
        elif time_unit == "d":
            duration += int(number) * 60 * 24
        elif time_unit == "w":
            duration += int(number) * 60 * 24 * 7

        cur_token = tokens.pop(0) if len(tokens) > 0 else None

    return duration


def format_duration(duration):
    """
    Format a duration in minutes into a friendly string like "1d 3h 32m"
    :param int duration: The duration in minutes
    :return: Formatted string.
    """
    weeks = duration / 10080
    weeks_r = duration % 10080
    days = weeks_r / 1440
    days_r = weeks_r % 1440
    hours = days_r / 60
    hours_r = days_r % 60
    minutes = hours_r

    segments = []
    segments.append(str(weeks) + "w") if weeks > 0 else None
    segments.append(str(days) + "d") if days > 0 else None
    segments.append(str(hours) + "h") if hours > 0 else None
    segments.append(str(minutes) + "m") if minutes > 0 else None

    return " ".join(segments)