from scrapy import Request

from generics.utils import extract_a
from generics.spiders import JAVSpider

from . import get_article, make_article
from .list_spider import ListSpider

ls_parse = ListSpider().parse


def studios(links):
    for url, t in extract_a(links):
        studio = make_article(get_article(url, t))

        yield studio
        yield Request(url, callback=ls_parse)


class StudioListSpider(JAVSpider):
    name = 'ave.studios'

    start_urls = (
        'http://aventertainments.com/studiolists.aspx?Dept_ID=29',
        'http://aventertainments.com/ppv/ppv_studiolists.aspx',
    )

    def parse(self, response):
        yield from studios(response.css('li.studio'))
        yield from studios(response.css('div.tb'))
