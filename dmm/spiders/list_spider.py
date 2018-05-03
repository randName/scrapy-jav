from generics.utils import extract_a
from generics.spiders import JAVSpider

from . import pagen


class ListSpider(JAVSpider):
    name = 'dmm.list'

    start_urls = (
        'http://www.dmm.co.jp/digital/videoa/-/list/=/sort=release_date/',
        'http://www.dmm.co.jp/mono/dvd/-/list/=/sort=date/',
    )

    def parse(self, response):
        export = response.meta.get('export')
        if export:
            yield {
                'url': response.url.split('?')[0]
            }
            return

        for url, t in extract_a(response.xpath(pagen)):
            try:
                yield response.follow(url, meta={'page': int(t)})
            except ValueError:
                pass

        for url, t in extract_a(response.xpath('//p[@class="tmb"]')):
            yield response.follow(url, meta={'export': True})
