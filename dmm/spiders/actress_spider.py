import re

from generics.utils import extract_a
from . import ArticleSpider, PAGEN

aiueo = '//table[@class="menu_aiueo"]'
alias_re = re.compile(r'(.+?)(?:[(（](.+?)[)）]?)?(?:（.+?）)?$')


class ActressSpider(ArticleSpider):
    name = 'dmm.actress'

    start_urls = (
        'http://www.dmm.co.jp/digital/videoa/-/actress/=/keyword=a/',
        'http://www.dmm.co.jp/mono/dvd/-/actress/=/keyword=a/',
    )

    pagination_xpath = PAGEN

    def export_part(self, response):
        for actress in response.css('div.act-box').xpath('.//li'):
            url, t = next(extract_a(actress))

            a = self.get_article(url, name=t)
            if a is None:
                continue

            name, alias = alias_re.match(t).groups()
            if alias is not None:
                a['name'] = name
                a['alias'] = alias

            a['image'] = actress.xpath('.//img/@src').extract_first()

            extra = actress.xpath('.//span/text()').extract()
            if extra:
                a['kana'], alias_kana = alias_re.match(extra[0]).groups()
                if alias_kana is not None:
                    a['alias_kana'] = alias_kana

                try:
                    a['count'] = int(extra[1].split('：')[1])
                except (IndexError, ValueError):
                    pass

            yield a

        for url, t in extract_a(response.xpath(aiueo)):
            yield response.follow(url)
