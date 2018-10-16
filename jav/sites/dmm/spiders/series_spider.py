from jav.utils import extract_a
from jav.spiders import JAVSpider

from ..article import get_article

desc_xp = './/div[@class="tx-work mg-b12 left"]/text()'
p_xp = '//div[@class="paginationControl" or contains(@class,"pagenation")]'


class SeriesSpider(JAVSpider):
    name = 'dmm.series'

    start_urls = (
        'http://www.dmm.co.jp/digital/videoa/-/series/',
        'http://www.dmm.co.jp/mono/dvd/-/series/',
    )

    pagination_xpath = '(%s)[1]' % p_xp

    def export_items(self, response):
        for cell in response.xpath('//td'):
            try:
                ln = extract_a(cell)
                next(ln)
                url, t = next(ln)
            except StopIteration:
                continue

            if not t or '=' not in url:
                continue

            desc = ''.join(cell.xpath(desc_xp).extract()).strip()

            item = get_article(url, name=t, description=desc)
            if item:
                item['url'] = response.urljoin(url)
                yield item
