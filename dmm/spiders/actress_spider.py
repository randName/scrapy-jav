import re

from generics.spiders import JAVSpider
from generics.utils import extract_a

from . import pagen, get_type
from . import get_article, article_json

aiueo = '//table[@class="menu_aiueo"]'
alias_re = re.compile(r'(.+?)(?:[(（](.+?)[)）]?)?(?:（.+?）)?$')


class ActressSpider(JAVSpider):
    name = 'dmm.actress'

    start_urls = (
        'http://www.dmm.co.jp/digital/videoa/-/actress/=/keyword=a/',
        'http://www.dmm.co.jp/mono/dvd/-/actress/=/keyword=a/',
    )

    def parse(self, response):
        v_type = get_type(response.url)

        for actress in response.css('div.act-box').xpath('.//li'):
            url, t = next(extract_a(actress))
            if v_type == 'digital':
                url = url[:-13]

            a = get_article(url, t)
            if a is None:
                continue

            name, alias = alias_re.match(t).groups()
            if alias is not None:
                a['name'] = name
                a['alias'] = alias

            extra = actress.xpath('.//span/text()').extract()
            if extra:
                a['kana'], alias_kana = alias_re.match(extra[0]).groups()
                if alias_kana is not None:
                    a['alias_kana'] = alias_kana

                try:
                    a['count'] = int(extra[1].split('：')[1])
                except (IndexError, ValueError):
                    pass

            a['image'] = actress.xpath('.//img/@src').extract_first()

            article_json(a)
            yield a

        for url, t in extract_a(response.xpath(pagen)):
            try:
                page = int(t)
                if page == 1:
                    continue
                yield response.follow(url, meta={'page': page})
            except ValueError:
                continue

        for url, t in extract_a(response.xpath(aiueo)):
            yield response.follow(url)
