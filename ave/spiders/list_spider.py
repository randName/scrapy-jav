from generics.spiders import ListSpider

from . import pagen


class AVEListSpider(ListSpider):
    name = 'ave.list'

    pagination_xpath = pagen
    export_xpath = '//div[@class="list-cover"]|//h3[not(@class)]'

    def ignore_url(self, url):
        return url == '#'

    def export_item(self, response):
        return {
            'url': response.url
        }
