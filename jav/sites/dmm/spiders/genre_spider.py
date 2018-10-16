from jav.spiders import JAVSpider

from ..article import get_article

xp = '(//table[@class="sect02"]|//div[@class="d-sect"]/ul)'
s_xp = '../preceding-sibling::div/text()'


class GenreSpider(JAVSpider):
    name = 'dmm.genre'

    start_urls = (
        'http://www.dmm.co.jp/digital/videoa/-/genre/',
        'http://www.dmm.co.jp/mono/dvd/-/genre/',
    )

    def export_items(self, response):
        for section in response.xpath(xp):
            sname = section.xpath('@summary').extract_first()
            if not sname:
                sname = section.xpath(s_xp).extract_first()

            if sname == 'おすすめジャンル':
                continue

            for a in section.xpath('.//a'):
                url, t = a.xpath('(@href|text())').extract()
                if url.startswith('#'):
                    continue

                item = get_article(url, name=t, category=sname)
                if item:
                    item['url'] = response.urljoin(url)
                    yield item
