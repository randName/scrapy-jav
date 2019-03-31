from jav.spiders import JAVSpider
from jav.utils import parse_range

from ..article import parse_article
from ..constants import REALMS, ARTICLES


class ArticleSpider(JAVSpider):
    name = 'dmm.article'

    def __init__(self, article=None, ids='', **kw):
        if article:
            self.article = {'article': article}
            self.range = set(parse_range(ids)) or range(100)
        else:
            self.article = None

    def start_requests(self):
        yield from super().start_requests()

        if self.article:
            a = self.article
            for i in self.range:
                a['id'] = i
                for r in REALMS:
                    yield self.make_request(ARTICLES.format(**a, **r))

    def export_items(self, response):
        yield parse_article(response)
