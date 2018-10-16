from jav.utils import parse_url, get_key

url_formats = {
    'DVD': {
        'video': ('product', 'product_id'),
        'studio':  ('studio', 'studioid'),
        'series':  ('series', 'seriesid'),
        'subdept': ('subdept', 'subdept_id'),
        'actress': ('actress', 'actressname'),
    },
    'PPV': {
        'video': ('ppv/new', 'proid'),
        'subdept': ('ppv/dept', 'cat_id'),
        'studio':  ('ppv/ppv_studio', 'studioid'),
        'series':  ('ppv/ppv_series', 'seriesid'),
        'actress': ('ppv/ppv_actress', 'actressname'),
    },
}


def parse_ave_url(url):

    def get_parts(p):
        shop = 'PPV' if p.startswith('ppv') else 'DVD'

        for t, a in url_formats[shop].items():
            if p.startswith(a[0]):
                return shop, t, a[1]

        return None, None, None

    path, query = parse_url(url.lower())
    shop, t, idk = get_parts(path[1:])

    if t is None:
        return {}

    _id = get_key(query, idk)

    try:
        _id = int(_id)
    except ValueError:
        _id = _id.replace(' ', '-')
    except TypeError:
        return {}

    return {
        'base': t,
        'id': _id,
        'shop': shop,
    }


def get_article(url, **article):
    a = parse_ave_url(url)

    if a.get('base', 'video') == 'video':
        return None

    article['article'] = a.pop('base')
    article.update(a)

    return article


def parse_article(response):
    item = response.meta.get('article') or get_article(response.url)
    if item is None:
        return

    name = response.xpath('//h3[@class="block"]/a/text()').extract_first()

    if not item.get('name'):
        item['name'] = name

    return item
