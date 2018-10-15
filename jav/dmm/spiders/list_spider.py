from generics.spiders import JAVSpider
from . import PAGEN


class ListSpider(JAVSpider):
    name = 'dmm.list'

    start_urls = (
        'http://www.dmm.co.jp/digital/videoa/-/list/=/sort=release_date/',
        'http://www.dmm.co.jp/mono/dvd/-/list/=/sort=date/',
    )

    pagination_xpath = PAGEN
    url_xpath = '//p[@class="tmb"]//a/@href'

    def export_item(self, response):
        for url in response.xpath(self.url_xpath).extract():
            yield {
                'url': url.split('?')[0],
            }
