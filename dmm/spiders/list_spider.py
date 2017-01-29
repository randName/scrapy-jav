from . import *


class ListSpider(DMMSpider):
    name = 'dmm.list'
    base_url = 'list'

    def __init__(self, article=None, ids=None, **kwargs):
        super().__init__(**kwargs)
        order = kwargs.get('sort', 'date')

        if not article or not ids:
            self.start_urls = {'article': '', 'id': '', 'sort': order},
        else:
            try:
                with open(ids, 'r') as f:
                    ids = tuple(a.split(',')[1] for a in f)
            except OSError:
                ids = ids.split(',')
            p = {'article': article, 'sort': order}
            self.start_urls = tuple({**p, 'id': i} for i in ids)

    def parse(self, response):
        for url in pagelist(response.css(pagediv)[0])[:-2]:
            yield Request(response.urljoin(url))

        for url in pagelist(response, selector='p.tmb'):
            yield VideoSpider.make_request(parse_url('video', url))
