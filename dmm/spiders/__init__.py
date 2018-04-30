# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.
from generics.utils import extract_a

ARTICLE_JSON_FILENAME = '{type}/articles/{article}/{id}.json'
ARTICLE_KEYS = ('article', 'id', 'type')

pagen = '(//div[contains(@class,"pagenation")])[1]'


def get_type(url):
    return 'mono' if 'mono/dvd' in url else 'digital'


def get_article(url, _type=True):
    article = tuple(i.split('=')[1] for i in url.split('/')[-3:-1])

    try:
        a_id = int(article[1])
    except (IndexError, ValueError):
        return None

    a_type = {'type': get_type(url)} if _type else {}

    return {
        'article': article[0],
        'id': a_id,
        **a_type,
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
        a = get_article(url, _type=False)
        if a is None:
            continue

        if only_id:
            yield a['id']
        else:
            yield a['article'], a['id']

        if urls is not None and url not in urls:
            a['name'] = t
            urls[url] = a
