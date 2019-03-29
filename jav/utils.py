class AttrDict(dict):
    """Access `dict` keys as attributes"""
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


def get_aux(url):
    """Get auxiliary page and return Selector"""
    from requests import get
    from scrapy.selector import Selector
    return Selector(text=get(url).text)


def extract_t(element, p='text()'):
    """Get stripped text of first element"""
    try:
        return element.xpath(p).get('').strip()
    except AttributeError:
        return ''


def extract_a(element, xpaths=('@href', 'text()')):
    """Get attributes of all a elements"""
    for e in element.xpath('.//a'):
        yield tuple(extract_t(e, i) for i in xpaths)


def parse_url(url):
    """Get the path and parsed query string"""
    from urllib.parse import urlparse, parse_qs

    u = urlparse(url)
    return u.path, parse_qs(u.query)


def get_key(url, key):
    """Get a key from the query string of a url"""
    if isinstance(url, dict):
        query = url
    else:
        query = parse_url(url)[1]

    return query.get(key, (None,))[0]
