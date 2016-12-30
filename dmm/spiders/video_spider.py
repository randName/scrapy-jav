import re

from scrapy import Spider, Request
from os.path import dirname, basename
from urllib.parse import urlsplit

from . import *

RTM_RE = re.compile(r'(\d+)分')
ART_RE = re.compile(r'article=(?P<article>\w+)/id=(?P<id>\d+)')
CID_RE = re.compile(r'/(?P<service>\w+)/(?P<shop>\w+)/-/detail/=/cid=(?P<cid>\w+)')


class VideoSpider(Spider):
    name = 'videos'

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

        p['sort'] = kwargs['sort'] if 'sort' in kwargs else 'release_date'

        s.start_urls = realm_urls('-/list/=/%s' % urlparams(**p), realm=(0,))

    def maker_urls(s, p):
        p['article'] = 'maker'
        with open ('makers_by_videocount','r') as f:
            makers = tuple( m.strip('\n') for m in f )

        for m in makers:
            p['id'] = m
            yield realm_urls('-/list/=/%s' % urlparams(**p), realm=(0,))[0]

    def parse(s, r):
        yield from pagelist(r.css('div.list-boxpagenation'), callback=s.parse)
        yield from pagelist(r, selector='p.tmb', callback=s.parse_video)

    def parse_mutual(s, r):
        related = tuple(s.safegroupdict(r.css(href).extract(), CID_RE))
        yield { 'related': related+(r.meta['item'],) }

    def parse_article(s, r):
        item = r.meta['item']
        span = r.css('p.headwithelem span::text').extract()
        item['name'] = ''.join(span[:2]).split('\xa0')[-1].strip('\n')
        yield item

    def parse_video(s, r):
        vid = {
            'title': r.css('h1::text').extract_first(),
            'description': s.get_description(r.css('div.mg-b20.lh4')),
            #'rating': r.css("div.d-review__points strong::text").extract(),
            'samples': len(r.css('a[id*=sample-image] %s' % isrc).extract()),
            'pkg': urlsplit(r.css('img.tdmm::attr(src)').extract_first()).path,
        }

        table = { k: v for k, v in s.get_table(r) }

        for rq in table['requests']:
            yield rq
        del table['requests']

        url = CID_RE.search(r.url).groupdict()
        u = r.urljoin('/misc/-/mutual-link/ajax-index/=/'+urlparams(**url))
        yield Request(u, callback=s.parse_mutual, meta={'item': url})

        #vid['samples_path'] = dirname(urlsplit(samples[0]).path)
        yield {**vid, **table}

    def safegroupdict(self, strings, pattern):
        for s in strings:
            try:
                yield pattern.search(s).groupdict()
            except AttributeError:
                print(s)
                pass

    def get_description(self, d):
        desc = d.css('p.mg-b20::text').extract_first()
        if not desc:
            desc = d.css('::text').extract_first()
        return desc.strip('\n')

    def get_articles(self, links):
        for l in links:
            try:
                a = ART_RE.search(l).groupdict()
                a['url'] = l
                yield a
            except (KeyError, TypeError, AttributeError):
                pass

    def get_table(s, r):
        m2m = ('actress', 'keyword', 'histrion')
        requests = []

        for row in r.css('div.page-detail table table tr'):
            articles = tuple(s.get_articles(row.css(href).extract()))

            for a in articles:
                requests.append(Request(r.urljoin(a['url']),
                    callback=s.parse_article, meta={'item': a}))

            if articles:
                a = articles[0]
                a_id = int(a['id'])
                if a['article'] in m2m:
                    a_id = tuple(int(a['id']) for a in articles)
                yield a['article'], a_id
                continue

            d = row.css('td::text').extract()
            try:
                yield 'runtime', int(RTM_RE.match(d[1]).group(1))
            except (IndexError, AttributeError):
                pass
            try:
                if d[0][-3:-1] == '売日':
                    date_str = d[1].strip('\n') if '/' in d[1] else ''
                    yield 'date', date_str.split('/')
            except (IndexError, KeyError):
                pass

        yield 'requests', requests
