# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.

from generics.utils import parse_url, get_key

pagen = '(//div[@class="pagination"])[1]'

articles = {
    'keyword': {
        'url': 'subdept',
        'key': 'subdept_id',
    },
    'actress': {
        'url': 'Actress',
        'key': 'actressname',
    },
    'studio': {
        'url': 'studio',
        'key': 'StudioID',
    },
    'series': {
        'url': 'Series',
        'key': 'SeriesID',
    },
}


def get_article(url, name):
    path, query = parse_url(url)
    p = path[1:]

    a_type = None
    a_key = None

    for t, a in articles.items():
        if p.startswith(a['url']):
            a_type = t
            a_key = a['key']
            break

    if a_type is None:
        return None

    a_id = get_key(query, a_key)

    return {
        'article': a_type,
        'name': name,
        'id': a_id,
    }
