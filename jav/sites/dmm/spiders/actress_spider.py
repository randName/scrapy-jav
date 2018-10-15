from jav.utils import extract_a
from jav.spiders import JAVSpider

from ..constants import PAGEN
from ..article import get_article

aiueo = '//table[@class="menu_aiueo"]'
alias_re = r'(.+?)(?:[(（](.+?)[)）]?)?(?:（.+?）)?$'


class ActressSpider(JAVSpider):
    name = 'dmm.actress'

    start_urls = (
        'http://www.dmm.co.jp/digital/videoa/-/actress/=/keyword=a/',
        'http://www.dmm.co.jp/mono/dvd/-/actress/=/keyword=a/',
    )

    pagination_xpath = PAGEN

    def parse_item(self, response):
        yield from self.links(response, aiueo, follow=True)

    def export_items(self, response):
        for actress in response.css('div.act-box').xpath('.//li'):
            url = actress.xpath('.//a/@href').extract_first()
            name, alias = actress.xpath('.//a/text()').re(alias_re)

            a = get_article(url, name=name)
            if a is None:
                continue

            if alias:
                a['alias'] = alias

            a['url'] = response.urljoin(url).split('sort')[0]
            a['image'] = actress.xpath('.//img/@src').extract_first()

            try:
                extra, count = actress.xpath('.//span/text()')
                try:
                    a['count'] = int(count.extract().split('：')[1])
                except (IndexError, ValueError):
                    pass

                a['kana'], alias_kana = extra.re(alias_re)
                if alias_kana:
                    a['alias_kana'] = alias_kana
            except ValueError:
                pass

            yield a
