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
            link = cell.xpath('(.//a)[2]')
            if not link:
                continue

            try:
                url, t = link.xpath('@href|text()').getall()
            except ValueError:
                continue

            item = get_article(url, name=t)
            if 'article' not in item:
                continue

            item['description'] = ''.join(cell.xpath(desc_xp).getall()).strip()
            item['url'] = response.urljoin(url)
            yield item
