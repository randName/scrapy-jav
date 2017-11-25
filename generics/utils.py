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
