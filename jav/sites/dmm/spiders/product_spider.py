from jav.spiders import JAVSpider
from jav.utils import parse_range

from ..video import parse_product

product_link = 'http://actress.dmm.co.jp/-/product/=/link_id=%d'


class ProductSpider(JAVSpider):
    name = 'dmm.product'

    def __init__(self, ids='', **kw):
        self.range = set(parse_range(ids)) or range(100)

    def start_requests(self):
        yield from super().start_requests()

        for i in self.range:
            yield self.make_request(product_link % i)

    def export_items(self, response):
        yield parse_product(response)
