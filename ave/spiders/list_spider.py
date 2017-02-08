from . import *


class StudioListSpider(AVESpider):
    name = 'ave.studio'
    base_url = 'studio'

    def __init__(self, ids=None, **kwargs):
        super().__init__(**kwargs)
        if not ids: return
        order = kwargs.get('sort', 1)

        try:
            with open(ids, 'r') as f:
                ids = tuple(a.split(',')[1] for a in f)
        except OSError:
            ids = ids.split(',')

            p = {'HowManyRecords': 200, 'SortBy': order}

            self.start_urls = tuple({**p, 'id': i} for i in ids)

    def parse(self, response):
        for url in pagelist(response.css('div.pagination')[0], selector='ol'):
            yield Request(response.urljoin(url))

        for url in pagelist(response, selector='h4'):
            yield VideoSpider.make_request(parse_url('video', url))
