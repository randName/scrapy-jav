from jav.spiders import JAVSpider
from . import PAGEN


class ListSpider(JAVSpider):
    name = 'ave.list'

    pagination_xpath = PAGEN

    def export_item(self, response):
        for url in response.xpath('//td/a[1]/@href').extract():
            yield {'url': url}
