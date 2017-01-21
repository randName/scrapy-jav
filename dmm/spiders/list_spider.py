from . import *


class ListSpider(DMMSpider):
    name = 'dmm.list'
    base_url = 'article'

    def __init__(self, article=None, ids=None, **kwargs):
        super().__init__(**kwargs)

        if not article or not ids:
            self.start_urls = { 'article': '', 'id': '' },
        else:
            try:
                with open(ids, 'r') as f:
                    ids = tuple(a.split(',')[1] for a in f)
            except OSError:
                ids = ids.split(',')
            self.start_urls = tuple({'article': article, 'id': i} for i in ids)

    def parse(self, response):
        for url in pagelist(response.css(pagediv)):
            yield Request(response.urljoin(url))

        for url in pagelist(response, selector='p.tmb'):
            yield VideoSpider.make_request(parse_url('video', url))
