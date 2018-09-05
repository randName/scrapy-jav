# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.
from generics.spiders import JAVSpider

shops = {
    'mono': 'mono/dvd',
    'digital': 'digital/videoa',
}

PAGEN = '(//div[contains(@class,"pagenation")])[1]'

performer_re = {
    'actress': r'.*\xa0(.+?)(?:[(（](.+?)[)）])?(?:\(([^)]+?)\))?$',
    'histrion': r'.*\xa0(.+?)(?:（(.+?)）)?(?:\(([^)]+?)\))?$',
}

article_url = 'http://www.dmm.co.jp/{shop}/-/list/=/article={article}/id={id}/'


class ArticleSpider(JAVSpider):
    name = 'dmm.article'

    handle_httpstatus_list = (404,)

    json_filename = '{shop}/articles/{article}/{id}.json'

    def start_requests(self):
        try:
            a = {'article': self.article}
        except AttributeError:
            for url in self.start_urls:
                yield Request(url=url)
            return

        try:
            begin = getattr(self, 'begin', 1)
            limit = getattr(self, 'limit', 10000)
        except ValueError:
            return

        from scrapy import Request

        for i in range(begin, limit):
            a['id'] = i
            for s in shops:
                a['shop'] = shops[s]
                yield Request(url=article_url.format(**a))

    def get_article(self, url, **article):
        for i in url.split('/'):
            try:
                k, v = i.split('=')
            except ValueError:
                if i in shops:
                    article['shop'] = i
                continue

            if k == 'id':
                try:
                    article['id'] = int(v)
                except ValueError:
                    return None
            elif k == 'article':
                article['article'] = v

        return article

    def export_part(self, response):
        item = response.meta.get('article') or self.get_article(response.url)
        if item is None:
            return

        span = response.xpath('string(//p[@class="headwithelem"]/span)')

        if not item.get('name', ''):
            item['name'] = span.re_first(r'.*\xa0(.+)$')

        kana = None
        alias = None
        article = item['article']

        if article in performer_re:
            item['name'], alias, kana = span.re(performer_re[article])
        elif article == 'director':
            item['name'], kana = span.re(r'.*\xa0(.+?)(?:\(([^)]+?)\))?$')

        if alias:
            item['alias'] = alias

        if kana:
            item['kana'] = kana

        ct = response.xpath(PAGEN).xpath('p/text()').re_first(r'([\d,]+)')
        if ct:
            item['count'] = int(ct.replace(',', ''))

        return (item,)
