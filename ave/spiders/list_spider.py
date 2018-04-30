from scrapy import Request

from generics.utils import extract_a
from generics.spiders import JAVSpider

from . import pagen
from .video_spider import VideoSpider

li = '//div[@class="list-cover"]|//h3[not(@class)]'

video_parse = VideoSpider().parse


class ListSpider(JAVSpider):
    name = 'ave.list'

    def parse(self, response):
        for url, t in extract_a(response.xpath(pagen)):
            if url == '#':
                continue
            try:
                yield Request(url, meta={'page': int(t)})
            except ValueError:
                continue

        for url, t in extract_a(response.xpath(li)):
            yield Request(url, callback=video_parse)
