def get_aux(url):
    """Get auxiliary page and return Selector"""
    import requests
    from scrapy.selector import Selector
    req = requests.get(url)
    return Selector(text=req.text)


def extract_t(element, p='text()'):
    """Get stripped text of first element"""
    try:
        return element.xpath(p).extract_first().strip()
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
