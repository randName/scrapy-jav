from generics.spiders import JAVSpider

from . import make_article


class ArticleSpider(JAVSpider):
    name = 'ave.article'

    def parse(self, response):
        article = make_article(response.meta)
        if article:
            yield article
