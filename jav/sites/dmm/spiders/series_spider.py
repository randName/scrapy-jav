from jav.spiders import JAVSpider

from ..article import get_article

p_xp = '//div[@class="paginationControl" or contains(@class,"pagenation")]'


class SeriesSpider(JAVSpider):
    name = 'dmm.series'

    start_urls = (
        'http://www.dmm.co.jp/digital/videoa/-/series/',
        'http://www.dmm.co.jp/mono/dvd/-/series/',
    )

    pagination_xpath = '(%s)[1]' % p_xp

    def export_items(self, response):
        for div in response.xpath('.//div[@class="tx-work mg-b12 left"]'):
            try:
                url, t = div.xpath('(p/a)[1]').xpath('@href|text()').getall()
            except ValueError:
                continue

            item = get_article(response.urljoin(url), name=t)
            if item is None:
                continue

            desc = ''.join(div.xpath('text()').getall()).strip()
            if desc:
                item['text'] = desc

            yield item
