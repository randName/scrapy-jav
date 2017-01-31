# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.

from datetime import date
from itertools import groupby
from scrapy import Spider, Request

from ave import realms, m2m, o2m, url_for, parse_url


def pagelist(links, selector='li'):
    return links.css(selector).xpath('a/@href').extract()


def get_params(base, links):
    for a in links.css('a'):
        url = a.xpath('@href').extract_first()
        params = parse_url(base, url)
        if params:
            yield {**params, 'name': a.xpath('text()').extract_first()}


class AVESpider(Spider):
    name = None
    base_url = ''

    custom_settings = {
        'ITEM_PIPELINES': {
            #'ave.pipelines.AvePipeline': 300,
        },
    }

    def __init__(self, realm='0', **kwargs):
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


class VideoSpider(AVESpider):
    name = 'ave.video'
    base_url = 'video'

    def __init__(self, vids=None, **kwargs):
        super().__init__(**kwargs)

        if vids is not None:
            self.start_urls = tuple({'id': int(vid)} for vid in vids.split(','))

    def parse(self, response):
        item = response.meta.get('params', {})

        maincontent = response.css('div.main-subcontent-page')
        detailbox = response.xpath('//div[@id="detailbox"]')

        #print(detailbox[0].xpath('ol').extract())

        related = tuple(get_params('video', response.xpath('//div[@id="mini-tabs"]')))
        articles = list(get_params('keyword', detailbox[1]))
        for k in (o2m+('actress',)):
            articles.extend(get_params(k, maincontent))

        #for a in articles: yield a

        table = {k: v for k, v in self.get_table(maincontent, articles)}

        vid = {
            'cid': response.css('div.top-title::text').re_first('商品番号: (.*)'),
            'title': response.css('h2::text').extract_first(),
        }

        #print({**item, **vid, **table})

    def get_table(self, table, articles):
        t = table.xpath('.//li/text()')

        try:
            yield 'runtime', int(t.re_first(r'(\d+) Min.'))
        except (TypeError, ValueError):
            pass

        dt = t.re(r'(\d+)/(\d+)/(\d+)')
        if dt:
            dt = (dt[2], dt[0], dt[1])
            yield 'date', date(*tuple(int(n) for n in dt))

        for article, l in groupby(articles, key=lambda x: x['article']):
            if article in m2m:
                a_id = set(a['id'] for a in l)
            else:
                a_id = next(l)['id']
            yield article, a_id
