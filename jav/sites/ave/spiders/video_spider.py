from jav.spiders import JAVSpider
from jav.spiders.list_spider import UrlListSpider

from ..video import parse_video
from ..constants import PAGEN


class VideoSpider(JAVSpider):
    name = 'ave.video'

    retry_xpath = '//h2'

    def export_items(self, response):
        yield parse_video(response)


class ListSpider(UrlListSpider):
    name = 'ave.list'

    pagination_xpath = PAGEN

    def export_items(self, response):
        yield parse_video(response)

    def get_list(self, response):
        yield from response.xpath('//td/a[1]/@href').extract()
