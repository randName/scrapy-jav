import os
import re

db_url = os.getenv('THZ_DATABASE_URL')

FQDN = 'http://taohuabbs.cc/' 

url_bases = {
    'forum': 'forum-{fid}-{page}.html',
    'thread': 'thread-{tid}-{page}-{_}.html',
}

_re = {
    k: r'(?P<%s>\d+)'%k for k in ('fid', 'tid', 'page', '_')
}

url_parsers = {
    k: re.compile(v.format(**_re)) for k, v in url_bases.items()
}

def url_for(base=None, **kwargs):
    return FQDN + url_bases.get(base, '').format(**kwargs)

def parse_url(base=None, url=''):
    try:
        return url_parsers[base].search(url).groupdict()
    except (KeyError, AttributeError):
        return {}
