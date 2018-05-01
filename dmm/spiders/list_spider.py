from scrapy import Request

from generics.utils import extract_a
from generics.spiders import JAVSpider

from . import pagen
from .video_spider import VideoSpider

video_parse = VideoSpider().parse


class ListSpider(JAVSpider):
    name = 'dmm.list'

    start_urls = (
        'http://www.dmm.co.jp/digital/videoa/-/list/=/sort=release_date/',
        'http://www.dmm.co.jp/mono/dvd/-/list/=/sort=date/',
    )

    def parse(self, response):
        for url, t in extract_a(response.xpath(pagen)):
            try:
                yield Request(response.urljoin(url), meta={'page': int(t)})
            except ValueError:
                pass

        for url, t in extract_a(response.xpath('//p[@class="tmb"]')):
            yield Request(url, callback=video_parse)
