from scrapy import Request

from generics.utils import extract_a
from generics.spiders import JAVSpider

from . import pagen, get_article, make_article
from .video_spider import VideoSpider

li = '//div[@class="list-cover"]|//h3[not(@class)]'


class StudioSpider(JAVSpider):
    name = 'ave.studio'
    video_parse = VideoSpider().parse

    def parse(self, response):
        studio = make_article(response.meta)
        if studio:
            yield studio

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
        'http://aventertainments.com/studiolists.aspx?Dept_ID=29',
        'http://aventertainments.com/ppv/ppv_studiolists.aspx',
    )

    def studios(self, links):
        for url, t in extract_a(links):
            a = get_article(url)
            a['name'] = t
            a['type'] = 'PPV' if 'ppv' in url else 'DVD'
            yield Request(url, meta=a, callback=self.studio_parse)

    def parse(self, response):
        yield from self.studios(response.css('li.studio'))
        yield from self.studios(response.css('div.tb'))
