from generics.utils import extract_a
from generics.spiders import ListSpider

from . import pagen


class DMMListSpider(ListSpider):
    name = 'dmm.list'

    start_urls = (
        'http://www.dmm.co.jp/digital/videoa/-/list/=/sort=release_date/',
        'http://www.dmm.co.jp/mono/dvd/-/list/=/sort=date/',
    )

    def pagination(self, response):
        for url, t in extract_a(response.xpath(pagen)):
            try:
                yield url, int(t)
            except ValueError:
                pass

    def export_links(self, response):
        for url, t in extract_a(response.xpath('//p[@class="tmb"]')):
            yield url

    def export_item(self, response):
        return {
            'url': response.url.split('?')[0]
        }
