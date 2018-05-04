from generics.spiders import ListSpider

from . import pagen


class DMMListSpider(ListSpider):
    name = 'dmm.list'

    start_urls = (
        'http://www.dmm.co.jp/digital/videoa/-/list/=/sort=release_date/',
        'http://www.dmm.co.jp/mono/dvd/-/list/=/sort=date/',
    )

    pagination_xpath = pagen
    export_xpath = '//p[@class="tmb"]'

    def export_item(self, response):
        return {
            'url': response.url.split('?')[0]
        }
