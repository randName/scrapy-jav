from scrapy import Request

from generics.spiders import JAVSpider
from generics.utils import extract_t, extract_a


class ThreadSpider(JAVSpider):
    name = 'thz.thread'

    def parse(self, response):
        print(response.url)


class ForumSpider(JAVSpider):
    name = 'thz.forum'
    thread_parse = ThreadSpider().parse

    def parse(self, response):
        for url, t in extract_a(response.xpath('//td[@class="num"]')):
            yield Request(response.urljoin(url), callback=self.thread_parse)

        for url, t in extract_a(response.xpath('(//div[@class="pg"])[1]')):
            try:
                yield Request(response.urljoin(url), meta={'page': int(t)})
            except ValueError:
                pass
