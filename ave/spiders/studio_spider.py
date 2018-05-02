from scrapy import Request

from generics.utils import extract_a
from generics.spiders import JAVSpider

from . import get_article, article_json
from .list_spider import ListSpider

ls_parse = ListSpider().parse


def studios(links):
    for url, t in extract_a(links):
        studio = get_article(url, t)
        article_json(studio)
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
