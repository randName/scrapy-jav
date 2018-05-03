from generics.utils import extract_a
from generics.spiders import JAVSpider

from . import pagen

li = '//div[@class="list-cover"]|//h3[not(@class)]'


class ListSpider(JAVSpider):
    name = 'ave.list'

    def parse(self, response):
        export = response.meta.get('export')
        if export:
            yield {
                'url': response.url
            }
            return

        for url, t in extract_a(response.xpath(pagen)):
            if url == '#':
                continue
            try:
                yield response.follow(url, meta={'page': int(t)})
            except ValueError:
                continue

        for url, t in extract_a(response.xpath(li)):
            yield response.follow(url, meta={'export': True})
