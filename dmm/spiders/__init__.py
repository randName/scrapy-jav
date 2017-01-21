# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.

from datetime import date
from itertools import groupby
from scrapy import Spider, Request

from dmm import m2m, realms, url_for, parse_url


p_script = '//script[contains(., "a#a_performer")]/text()'

pagediv = 'div.list-boxpagenation'

def keyf(x): return x['article']

def pagelist(links, selector='li'):
    return links.css(selector).xpath('a/@href').extract()

def get_params(base, links):
    for a in links.css('a'):
        url = a.xpath('@href').extract_first()
        params = parse_url(base, url)
        if params:
            yield {**params, 'name': a.xpath('text()').extract_first()}

def get_articles(articles):
    for a in articles:
        a['id'] = int(a['id'])
        yield a


class DMMSpider(Spider):
    name = None
    base_url = ''

    custom_settings = {
        'ITEM_PIPELINES': {
            'dmm.pipelines.DmmPipeline': 300,
            'dmm.pipelines.DatabasePipeline': 400,
            'dmm.pipelines.AriaPipeline': 500,
        },
    }

    def __init__(self, realm=None, **kwargs):
        super().__init__(**kwargs)

        try:
            self.realm = realms[realm],
        except KeyError:
            self.realm = realms.values()

    def start_requests(self):
        for r in self.realm:
            for u in self.start_urls:
                p = {**r, **u}
                yield Request(url_for(self.base_url, **p), meta={'params': p})

    @classmethod
    def make_request(cls, params):
        if not params: return
        url = url_for(cls.base_url, **params)
        return Request(url, callback=cls().parse, meta={'params': params})


class MutualSpider(DMMSpider):
    name = 'dmm.mutual'
    base_url = 'mutual'

    def __init__(self, cids=None, **kwargs):
        super().__init__(**kwargs)

        if cids is not None:
            self.start_urls = tuple({'cid': cid} for cid in cids.split(','))

    def parse(self, response):
        item = response.meta.get('params', {})
        yield {'mutual': tuple(get_params('video', response)) + (item,)}


class ArticleSpider(DMMSpider):
    name = 'dmm.article'
    base_url = 'article'

    def __init__(self, article=None, ids=None, **kwargs):
        if article is None or ids is None: return
        super().__init__(**kwargs)
        ids = set(int(i) for i in ids.split(','))
        self.start_urls = tuple({'article': article, 'id': i} for i in ids)

    def parse(self, response):
        item = response.meta.get('params', {})

        if 'name' not in item:
            span = response.css('p.headwithelem span::text').extract()
            item['name'] = ''.join(span[:2]).split('\xa0')[-1].strip('\n')

        ct = response.css(pagediv).css('p::text').re_first(r'([0-9,]+)')
        if ct:
            item['count'] = int(ct.replace(',',''))

        yield item


class VideoSpider(DMMSpider):
    name = 'dmm.video'
    base_url = 'video'

    def __init__(self, cids=None, **kwargs):
        super().__init__(**kwargs)

        if cids is not None:
            self.start_urls = tuple({'cid': cid} for cid in cids.split(','))

    def parse(self, response):
        item = response.meta.get('params', {})
        table_css = response.css('div.page-detail table table tr')
        articles = sorted(get_params('article', table_css), key=keyf)
        yield from get_articles(articles)
        table = { k: v for k, v in self.get_table(table_css, articles) }

        desc = response.css('div.mg-b20.lh4').xpath('string(.)')

        vid = {
            'title': response.css('h1::text').extract_first(),
            'description': desc.extract_first().strip('\n'),
        }
        #rating:response.css('div.d-review__points strong::text').extract()

        samples = response.css('a[id*=sample-image]').xpath('img/@src').extract()
        pic_css = response.css('img.tdmm::attr(src)').extract_first()
        pid = parse_url('pics', pic_css).get('pid')

        if samples:
            smp = parse_url('pics', samples[0])
            if not pid:
                pid = smp.get('pid')
            if smp.get('service') == item['service']:
                vid['samples'] = len(samples)

        if pid:
            vid['pid'] = pid

        yield MutualSpider.make_request(item)

        a_performer = response.xpath(p_script).re_first(r"url: '(.*)',")
        if a_performer:
            a_p = response.urljoin(a_performer)
            yield Request(a_p, callback=self.performers, meta={'params': item})

        yield {**item, **vid, **table}

    def performers(self, response):
        ps = sorted(get_params('article', response), key=keyf)
        yield from get_articles(ps)

        i = {m: set(a['id'] for a in l) for m, l in groupby(ps, key=keyf)}
        yield {**i, **response.meta.get('params', {})}

    def get_table(self, table, articles):
        t = table.xpath('td/text()')

        try:
            yield 'runtime', int(t.re_first(r'(\d+)分'))
        except (TypeError, ValueError):
            pass

        dt = t.re(r'(\d+)/(\d+)/(\d+)')
        if dt:
            yield 'date', date(*tuple(int(n) for n in dt))

        for article, l in groupby(articles, key=keyf):
            if article in m2m:
                a_id = set(a['id'] for a in l)
            else:
                a_id = next(l)['id']
            yield article, a_id
