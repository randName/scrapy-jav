from scrapy import Request

from generics.utils import extract_a
from generics.spiders import JAVSpider

from . import pagen
from .video_spider import VideoSpider

li = '//div[@class="list-cover"]|//h3[not(@class)]'


class StudioSpider(JAVSpider):
    name = 'ave.studio'
    video_parse = VideoSpider().parse

    def parse(self, response):
        if 'page' not in response.meta:
            l, name = next(extract_a(response.xpath('//h3[@class="block"]')))

        for url, t in extract_a(response.xpath(pagen)):
            if url == '#':
                continue
            try:
                yield Request(url, meta={'page': int(t)})
            except ValueError:
                continue

        for url, t in extract_a(response.xpath(li)):
            yield Request(url, callback=self.video_parse)


class StudioListSpider(JAVSpider):
    name = 'ave.studios'
    studio_parse = StudioSpider().parse

    start_urls = (
        'http://aventertainments.com/studiolists.aspx',
        'http://aventertainments.com/ppv/ppv_studiolists.aspx',
    )

    def parse(self, response):
        for url, t in extract_a(response.css('li.studio')):
            yield Request(url, callback=self.studio_parse)

        for url, t in extract_a(response.css('div.tb')):
            yield Request(url, callback=self.studio_parse)
