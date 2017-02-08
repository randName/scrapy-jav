import os
import re
from urllib.parse import urlsplit, parse_qsl, urlunsplit, urlencode

db_url = os.getenv('AVE_DATABASE_URL')

realms = {
    '0': { 'languageID': 2, 'Dept_ID': 29 },
    '1': { 'languageID': 2, 'VODTypeID': 1 },
}

o2m = ('studio', 'series')
m2m = ('actress', 'keyword')

url_bases = {
    'video': 'product_lists.aspx',
    'studio': 'studio_products.aspx',
    'series': 'Series.aspx',
    'keyword': 'subdept_products.aspx',
    'actress': 'ActressDetail.aspx',
    'studios': 'studiolists.aspx',
    'keywords': 'categorylists.aspx',
    'imgs': 'new/{param}/{pid}.jpg'
}

url_params = {
    'video': 'product_id',
    'studio': 'StudioID',
    'series': 'SeriesID',
    'keyword': 'subdept_id',
    'actress': 'actressname',
}


def url_for(base=None, **kwargs):
    if base == 'imgs':
        sub = 'imgs'
        url = (url_bases['imgs'].format(**kwargs), '', '')
    else:
        sub = 'www'
        k = url_params.get(base)
        if k and 'id' in kwargs:
            kwargs[k] = kwargs['id']
            for k in ('id', 'article'):
                kwargs.pop(k, None)
        url = (url_bases.get(base, ''), urlencode(kwargs), '')
    return urlunsplit(('http', '{sub}.aventertainments.com'.format(sub=sub)) + url)


def parse_url(base=None, url=''):
    u = urlsplit(url)
    if url_bases.get(base, '') in u.path:
        d = dict(parse_qsl(u.query))
        k = url_params.get(base)
        if k in d:
            try:
                d['id'] = int(d[k])
            except ValueError:
                d['id'] = d[k]
            d['article'] = base
            del d[k]
        return d
    else:
        return {}
