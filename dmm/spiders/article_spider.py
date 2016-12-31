from scrapy import Spider
from . import *


class ArticleSpider(Spider):
    name = 'article'

    def __init__(s, *args, **kwargs):
        super().__init__(*args, **kwargs)

        try:
            r = int(kwargs['realm']),
        except (KeyError, ValueError):
            r = None

        try:
            p = { a: kwargs[a] for a in ('article', 'id') }
        except KeyError:
            p = {}

        s.start_urls = realm_urls('-/list/=/%s' % urlparams(**p), realm=r)

    def parse(s, r):
        item = r.meta['item'] if 'item' in r.meta else {}

        if 'id' not in item:
            try:
                i = ART_RE.search(r.url).groupdict()
            except AttributeError:
                return
            for k, v in i.items():
                item[k] = v

        if 'name' not in item:
            span = r.css('p.headwithelem span::text').extract()
            item['name'] = ''.join(span[:2]).split('\xa0')[-1].strip('\n')

        count = r.css('div.list-boxpagenation p::text').extract_first()
        try:
            item['count'] = int(re.match(r'(\d+)', count.replace(',','')).group(1))
        except (ValueError, AttributeError):
            item['count'] = 0

        yield item
