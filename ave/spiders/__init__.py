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

article_formats = {
    'keyword': {
        'DVD': ('subdept', 'subdept_id'),
        'PPV': ('ppv/Dept', 'Cat_ID'),
    },
    'actress': {
        'DVD': ('Actress', 'actressname'),
        'PPV': ('ppv/ppv_Actress', 'actressname'),
    },
    'studio': {
        'DVD': ('studio', 'StudioID'),
        'PPV': ('ppv/ppv_studio', 'StudioID'),
    },
    'series': {
        'DVD': ('Series', 'SeriesID'),
        'PPV': ('ppv/ppv_series', 'SeriesID'),
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

    for t, a in article_formats.items():
        for a_type, base in a.items():
            if p.startswith(base[0]):
                return t, base[1], a_type

    return None, None, None


def get_article(url, name=None):
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

    a_name = {'name': name} if name is not None else {}

    return {
        'article': article,
        'type': a_type,
        'id': a_id,
        **a_name,
    }


def make_article(a):
    try:
        item = {k: a[k] for k in ARTICLE_KEYS}
        name = a.get('name', '')
        if name:
            item['name'] = name
        return item
    except KeyError:
        return None


def get_articles(links, urls=None, only_id=True):
    for url, t in extract_a(links):
        if url.startswith('javascript:'):
            continue

        a = get_article(url, t)
        if a is None:
            continue

        if urls is not None and url not in urls:
            urls[url] = a

        if only_id:
            yield a['id']
        else:
            yield a['article'], a['id']


def article_json(item):
    item['JSON_FILENAME'] = ARTICLE_JSON_FILENAME
