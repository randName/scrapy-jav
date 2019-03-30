from jav.spiders import JAVSpider

from ..article import get_article
from ..constants import PAGEN, AIUEO

alias_re = r'(.+?)(?:[(（](.+?)[)）]?)?(?:（.+?）)?$'


class ActressSpider(JAVSpider):
    name = 'dmm.actress.old'

    start_urls = (
        'http://www.dmm.co.jp/digital/videoa/-/actress/=/keyword=nn/',
        'http://www.dmm.co.jp/mono/dvd/-/actress/=/keyword=nn/',
    )

    pagination_xpath = PAGEN

    def parse_item(self, response):
        yield from super().parse_item(response)
        yield from self.links(response, AIUEO, follow=True)

    def export_items(self, response):
        for actress in response.css('div.act-box').xpath('.//li'):
            url = actress.xpath('.//a/@href').get()
            name, alias = actress.xpath('.//a/text()').re(alias_re)

            a = get_article(url, name=name)
            if a is None:
                continue

            if alias:
                a['alias'] = alias

            a['url'] = response.urljoin(url).split('sort')[0]
            a['image'] = actress.xpath('.//img/@src').get()

            try:
                extra, count = actress.xpath('.//span/text()')
                a['kana'], alias_kana = extra.re(alias_re)
                if alias_kana:
                    a['alias_kana'] = alias_kana
            except ValueError:
                pass

            yield a
