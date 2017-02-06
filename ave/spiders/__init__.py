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
        if 'id' in params:
            yield {**params, 'name': a.xpath('text()').extract_first()}


class AVESpider(Spider):
    name = None
    base_url = ''

    custom_settings = {
        'ITEM_PIPELINES': {
            'ave.pipelines.AvePipeline': 300,
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
        base = cls.base_url or params.get('article')
        url = url_for(base, **params)
        return Request(url, callback=cls().parse, meta={'params': params})


from .article_spider import ArticleSpider
