from generics.spiders import JAVSpider

from . import get_article, make_article

name_xp = '//h3[@class="block"]/a/text()'
idol_xp = '//span[@class="idol-link"]/a/@href'


class ArticleSpider(JAVSpider):
    name = 'ave.article'

    def parse(self, response):
        item = make_article(response.meta) or get_article(response.url)
        if item is None:
            return

        article = item['article']
        name = response.xpath(name_xp).extract_first()

        if article == 'actress':
            url = response.xpath(idol_xp).extract_first()
            if url is not None:
                a = get_article(url)
                item['id'] = a['id']

            if name and name.startswith('STARRING'):
                name = name.split(' >> ')[1]

        if not item.get('name', ''):
            item['name'] = name

        yield item
