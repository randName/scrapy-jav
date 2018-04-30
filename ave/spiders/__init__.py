# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.
from generics.utils import parse_url, get_key, extract_a

ARTICLE_JSON_FILENAME = '{type}/articles/{article}/{id}.json'
ARTICLE_KEYS = ('type', 'article', 'id')

pagen = '(//div[@class="pagination"])[1]'

pid_formats = {
    'DVD': ('product', 'product_id'),
    'PPV': ('ppv/new', 'ProID'),
}

articles = {
    'keyword': {
        'formats': {
            'DVD': ('subdept', 'subdept_id'),
            'PPV': ('ppv/Dept', 'Cat_ID'),
        },
        'parse': int,
    },
    'actress': {
        'formats': {
            'DVD': ('Actress', 'actressname'),
            'PPV': ('ppv/ppv_Actress', 'actressname'),
        },
        'parse': str,
    },
    'studio': {
        'formats': {
            'DVD': ('studio', 'StudioID'),
            'PPV': ('ppv/ppv_studio', 'StudioID'),
        },
        'parse': int,
    },
    'series': {
        'formats': {
            'DVD': ('Series', 'SeriesID'),
            'PPV': ('ppv/ppv_series', 'SeriesID'),
        },
        'parse': int,
    },
}


def get_pid(url):
    path, query = parse_url(url)
    p = path[1:]

    for t, v in pid_formats.items():
        if p.startswith(v[0]):
            try:
                return t, int(get_key(query, v[1]))
            except ValueError:
                pass

    return None, None


def identify_article(path):
    p = path[1:]

    for t, a in articles.items():
        for a_type, base in a['formats'].items():
            if p.startswith(base[0]):
                return t, base[1], a_type

    return None, None, None


def get_article(url):
    path, query = parse_url(url)
    article, a_key, a_type = identify_article(path)

    if article is None:
        return None

    a_id = get_key(query, a_key)

    try:
        a_id = int(a_id)
    except ValueError:
        a_id = a_id.replace(' ', '-')
    except TypeError:
        return None

    return {
        'article': article,
        'type': a_type,
        'id': a_id,
    }


def make_article(a):
    try:
        item = {k: a[k] for k in ARTICLE_KEYS}
        item['name'] = a.get('name', '')
        item['JSON_FILENAME'] = ARTICLE_JSON_FILENAME.format(**item)
        return item
    except KeyError:
        return None


def get_articles(links, urls=None, only_id=True):
    for url, t in extract_a(links):
        if url.startswith('javascript:'):
            continue

        a = get_article(url)
        if a is None:
            continue

        if only_id:
            yield a['id']
        else:
            yield a['article'], a['id']

        if urls is not None and url not in urls:
            a['name'] = t
            urls[url] = a
