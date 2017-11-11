from scrapy import Request

from generics.spiders import JAVSpider
from generics.utils import extract_t, extract_a

from .video_spider import get_articles
from .article_spider import ArticleSpider


def makers(element, titlep, descp):
    for mk in element:
        try:
            i = next(get_articles(mk))
        except StopIteration:
            continue

        yield {
            'id': i,
            'name': extract_t(mk.xpath(titlep)),
            'description': extract_t(mk.xpath(descp)),
            'image': mk.xpath('.//img/@src').extract_first(),
        }


class MakerSpider(JAVSpider):
    name = 'dmm.maker'
    article_parse = ArticleSpider().parse

    start_urls = (
        'http://www.dmm.co.jp/digital/videoa/-/maker/=/keyword=a/',
        'http://www.dmm.co.jp/mono/dvd/-/maker/=/keyword=a/',
    )

    def parse(self, response):

        if 'mono' in response.url:
            mora = '(//td[@class="makerlist-box-t2" or @class="initial"])'
            makerlist = '//td[@class="w50"]'
            titlep = './/a[@class="bold"]'
            descp = './/div[@class="maker-text"]'
            subt = '(//table[contains(@class,"list-table")]//tr)[position()>1]'
            yield from makers(response.xpath(subt), 'td/a', '(td)[2]')
        else:
            mora = '(//ul[starts-with(@class,"d-mod")])[position()>1]'
            makerlist = '//div[@class="d-unit"]'
            titlep = './/span[@class="d-ttllarge"]'
            descp = './/p'
            subt = None

        yield from makers(response.xpath(makerlist), titlep, descp)

        for url, t in extract_a(response.xpath(mora)):
            yield Request(response.urljoin(url))
