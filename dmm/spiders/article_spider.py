from scrapy import Request

from generics.spiders import JAVSpider

from . import pagen, get_article, make_article
from . import type_formats

types = type_formats.values()

article_url = 'http://www.dmm.co.jp/{type}/-/list/=/article={article}/id={id}/'

performer_re = {
    'actress': r'.*\xa0(.+?)(?:[(（](.+?)[)）])?(?:\(([^)]+?)\))?$',
    'histrion': r'.*\xa0(.+?)(?:（(.+?)）)?(?:\(([^)]+?)\))?$',
}


class ArticleSpider(JAVSpider):
    name = 'dmm.article'

    handle_httpstatus_list = (404,)

    def start_requests(self):
        article = self.custom_settings.get('article')
        if article is None:
            for url in self.start_urls:
                yield Request(url=url)
        else:
            try:
                begin = int(self.custom_settings.get('begin', 1))
            except ValueError:
                begin = 1

            try:
                limit = int(self.custom_settings.get('limit', 10000))
            except ValueError:
                limit = 10000

            p = {'article': article}
            for i in range(begin, limit):
                p['id'] = i
                for t in types:
                    p['type'] = t
                    yield Request(url=article_url.format(**p))

    def parse(self, response):
        if response.status == 404:
            return

        item = make_article(response.meta) or get_article(response.url)
        if item is None:
            return

        item = make_article(item)
        article = item['article']

        span = response.xpath('string(//p[@class="headwithelem"]/span)')

        if not item.get('name', ''):
            item['name'] = span.re_first(r'.*\xa0(.+)$')

        if article in performer_re:
            item['name'], alias, kana = span.re(performer_re[article])
        elif article == 'director':
            alias = None
            item['name'], kana = span.re(r'.*\xa0(.+?)(?:\(([^)]+?)\))?$')

        if alias:
            item['alias'] = alias

        if kana:
            item['kana'] = kana

        ct = response.xpath(pagen).xpath('p/text()').re_first(r'([\d,]+)')
        if ct:
            item['count'] = int(ct.replace(',', ''))

        yield item
