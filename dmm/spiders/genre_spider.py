from generics.utils import extract_a
from . import ArticleSpider

xp = '//div[@class="sect01" or @class="d-area area-list"]'
s_xp = 'div[@class="d-capt"]/text()'


class GenreSpider(ArticleSpider):
    name = 'dmm.genre'

    start_urls = (
        'http://www.dmm.co.jp/digital/videoa/-/genre/',
        'http://www.dmm.co.jp/mono/dvd/-/genre/',
    )

    def export_item(self, response):
        for section in response.xpath(xp)[1:]:
            sname = section.xpath('table/@summary').extract_first()
            if not sname:
                sname = section.xpath(s_xp).extract_first()

            for url, t in extract_a(section):
                if url.startswith('#'):
                    continue

                item = self.get_article(url, name=t)
                if item is None:
                    continue

                item['category'] = sname
                yield item
