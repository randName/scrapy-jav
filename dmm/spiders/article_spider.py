from generics.spiders import JAVSpider

from . import pagen, get_article, make_article


class ArticleSpider(JAVSpider):
    name = 'dmm.article'

    def parse(self, response):
        item = make_article(response.meta) or get_article(response.url)
        if item is None:
            return

        article = item['article']

        span = response.xpath('string(//p[@class="headwithelem"]/span)')

        if not item.get('name', ''):
            item['name'] = span.re_first(r'.*\xa0(.+)$')

        if article in ('actress', 'histrion', 'director'):
            title = span.re(r'.*\xa0(.+?)(?:（(.+?)[)）])?(?:\((.+?)\))?$')
            item['name_parsed'] = title[0]

            if title[1]:
                item['alias'] = title[1]

            if title[2]:
                item['kana'] = title[2]

        ct = response.xpath(pagen).xpath('p/text()').re_first(r'([\d,]+)')
        if ct:
            item['count'] = int(ct.replace(',', ''))

        yield item
