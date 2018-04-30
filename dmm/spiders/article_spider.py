from generics.spiders import JAVSpider

from . import pagen

JSON_FILENAME = 'articles/{article}/{id}.json'


class ArticleSpider(JAVSpider):
    name = 'dmm.article'

    def parse(self, response):
        try:
            article = response.meta['article']
        except KeyError:
            return

        item = {
            'article': article,
            'id': response.meta.get('id', 0),
        }

        span = response.xpath('string(//p[@class="headwithelem"]/span)')

        item['name'] = span.re_first(r'.*\xa0(.+)$')

        if article in ('actress', 'histrion', 'director'):
            title = span.re(r'.*\xa0(.+?)(?:（(.+?)）)?(?:\((.+?)\))?$')
            item['name_parsed'] = title[0]

            if title[1]:
                item['alias'] = title[1]

            if title[2]:
                item['kana'] = title[2]

        ct = response.xpath(pagen).xpath('p/text()').re_first(r'([\d,]+)')
        if ct:
            item['count'] = int(ct.replace(',', ''))

        item['JSON_FILENAME'] = JSON_FILENAME.format(**item)

        yield item
