from jav.spiders import JAVSpider

from ..article import parse_article
from ..constants import REALMS, ARTICLES


class ArticleSpider(JAVSpider):
    name = 'dmm.article'

    def __init__(self, article=None, **kw):
        if article:
            try:
                begin = int(kw.pop('begin', ''))
            except ValueError:
                begin = 1

            try:
                limit = int(kw.pop('limit', ''))
            except ValueError:
                limit = 100

            self.article = {
                'article': article,
                'begin': begin,
                'limit': limit,
            }
        else:
            self.article = None

    def start_requests(self):
        yield from super().start_requests()

        if self.article:
            a = self.article
            for i in range(a.pop('begin'), a.pop('limit')):
                a['id'] = i
                for r in REALMS:
                    yield self.make_request(ARTICLES.format(**a, **r))

    def export_items(self, response):
        yield parse_article(response)
