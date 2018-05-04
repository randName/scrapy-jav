from generics.utils import extract_a
from generics.spiders import ListSpider

from . import pagen

li = '//div[@class="list-cover"]|//h3[not(@class)]'


class AVEListSpider(ListSpider):
    name = 'ave.list'

    def pagination(self, response):
        for url, t in extract_a(response.xpath(pagen)):
            if url == '#':
                continue
            try:
                yield url, int(t)
            except ValueError:
                continue

    def export_links(self, response):
        for url, t in extract_a(response.xpath(li)):
            yield url

    def export_item(self, response):
        return {
            'url': response.url
        }
