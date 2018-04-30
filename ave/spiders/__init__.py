# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.
from generics.utils import parse_url, get_key

ARTICLE_KEYS = ('type', 'article', 'id', 'name')
ARTICLE_JSON_FILENAME = '{type}/articles/{article}/{id}.json'

pagen = '(//div[@class="pagination"])[1]'

pid_formats = {
    'DVD': ('product', 'product_id'),
    'PPV': ('ppv/new', 'ProID'),
}

articles = {
    'keyword': {
        'formats': (
            ('subdept', 'subdept_id'),
            ('ppv/Dept', 'Cat_ID'),
        ),
        'parse': int,
    },
    'actress': {
        'formats': (
            ('Actress', 'actressname'),
            ('ppv/ppv_Actress', 'actressname'),
        ),
        'parse': str,
    },
    'studio': {
        'formats': (
            ('studio', 'StudioID'),
            ('ppv/ppv_studio', 'StudioID'),
        ),
        'parse': int,
    },
    'series': {
        'formats': (
            ('Series', 'SeriesID'),
            ('ppv/ppv_series', 'SeriesID'),
        ),
        'parse': int,
    },
}


def get_pid(url):
    path, query = parse_url(url)
    p = path[1:]

    for t, v in pid_formats.items():
        if p.startswith(v[0]):
            return t, get_key(query, v[1])

    return None, None


def identify_type(path):
    p = path[1:]

    for t, a in articles.items():
        for base, key in a['formats']:
            if p.startswith(base):
                return t, key

    return None, None


def get_article(url):
    path, query = parse_url(url)
    a_type, a_key = identify_type(path)

    if a_type is None:
        return None

    a_id = get_key(query, a_key)

    try:
        a_id = int(a_id)
    except ValueError:
        a_id = a_id.replace(' ', '-')
    except TypeError:
        return None

    return {
        'article': a_type,
        'id': a_id,
    }


def make_article(a):
    try:
        item = {k: a[k] for k in ARTICLE_KEYS}
        item['JSON_FILENAME'] = ARTICLE_JSON_FILENAME.format(**item)
        return item
    except KeyError:
        return None
