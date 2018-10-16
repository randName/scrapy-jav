from jav.spiders import JAVSpider

from ..video import parse_video
from ..constants import PAGEN


class VideoSpider(JAVSpider):
    name = 'ave.video'

    retry_xpath = '//h2'

    def export_items(self, response):
        yield parse_video(response)


class ListSpider(JAVSpider):
    name = 'ave.list'

    pagination_xpath = PAGEN

    def __init__(self, deep=False):
        self.deep = deep

    def parse_item(self, response):
        urls = response.xpath('//td/a[1]/@href').extract()

        if self.deep:
            for url in urls:
                yield response.follow(url, meta={'deep': True})
        else:
            for url in urls:
                yield {'url': url}

    def export_items(self, response):
        if response.meta.get('deep'):
            yield parse_video(response)
