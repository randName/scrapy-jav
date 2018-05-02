from generics.spiders import JAVSpider
from generics.utils import extract_a

from . import get_type
from . import get_article, article_json


class GenreSpider(JAVSpider):
    name = 'dmm.genre'

    start_urls = (
        'http://www.dmm.co.jp/digital/videoa/-/genre/',
        'http://www.dmm.co.jp/mono/dvd/-/genre/',
    )

    def parse(self, response):
        if get_type(response.url) == 'mono':
            xp = '//div[@class="sect01"]'
            s_xp = 'table/@summary'
        else:
            xp = '//div[@class="d-area area-list"]'
            s_xp = 'div[@class="d-capt"]/text()'

        for section in response.xpath(xp)[1:]:
            sname = section.xpath(s_xp).extract_first()

            for url, t in extract_a(section):
                if url.startswith('#'):
                    continue

                item = get_article(url, t)
                if item is None:
                    continue

                item['category'] = sname

                article_json(item)
                yield item
