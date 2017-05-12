# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.

from datetime import date
from itertools import groupby
from scrapy import Spider, Request

from thz import url_for, parse_url


def pagelist(links, selector='li'):
    return links.css(selector).xpath('a/@href').extract()


def get_params(base, links):
    for a in links.css('a'):
        url = a.xpath('@href').extract_first()
        params = parse_url(base, url)
        if 'id' in params:
            yield {**params, 'name': a.xpath('text()').extract_first()}


class THZSpider(Spider):
    name = None
    base_url = ''

    custom_settings = {
    }

    def start_requests(self):
        for u in self.start_urls:
            yield Request(url_for(self.base_url, **u), meta={'params': u})

    @classmethod
    def make_request(cls, params):
        if not params: return
        base = cls.base_url or None
        url = url_for(base, **params)
        return Request(url, callback=cls().parse, meta={'params': params})
