# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.
from generics.utils import extract_a

ARTICLE_JSON_FILENAME = '{type}/articles/{article}/{id}.json'
ARTICLE_KEYS = ('article', 'id', 'type')

pagen = '(//div[contains(@class,"pagenation")])[1]'

type_formats = {
    'mono': 'mono/dvd',
    'digital': 'digital/videoa',
}


def get_type(url):
    return 'mono' if 'mono/dvd' in url else 'digital'


def get_article(url, name=None, _type=True):
    article = tuple(i.split('=')[1] for i in url.split('/')[-3:-1])

    try:
        a_id = int(article[1])
    except (IndexError, ValueError):
        return None

    a_type = {'type': get_type(url)} if _type else {}
    a_name = {'name': name} if name is not None else {}

    return {
        'article': article[0],
        'id': a_id,
        **a_name,
        **a_type,
    }


def get_articles(links, urls=None, only_id=True):
    for url, t in extract_a(links):
        a = get_article(url, t, _type=False)
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
