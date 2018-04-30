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
        'm2m': True,
        'parse': int,
    },
    'actress': {
        'url': 'Actress',
        'key': 'actressname',
        'm2m': True,
        'parse': str,
    },
    'studio': {
        'url': 'studio',
        'key': 'StudioID',
        'm2m': False,
        'parse': int,
    },
    'series': {
        'url': 'Series',
        'key': 'SeriesID',
        'm2m': False,
        'parse': int,
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


def process_articles(inp):
    sets = {k: set() for k in articles.keys()}

    for a in inp:
        if a is None:
            continue
        sets[a['article']].add(a['id'])

    for k, v in sets.items():
        a_type = articles[k]
        parse = a_type['parse']

        if a_type['m2m']:
            yield k, tuple(sorted(parse(a) for a in v))
        else:
            try:
                yield k, parse(v.pop())
            except KeyError:
                pass
