from scrapy import Request

from generics.spiders import JAVSpider
from generics.utils import extract_t, extract_a

from . import get_type, get_article, make_article
from .list_spider import ListSpider

ls_parse = ListSpider().parse

subt_main = '(//table[contains(@class,"list-table")]//tr)[position()>1]'


def makers(response, xp):
    for mk in response.xpath(xp.pop('main')):
        url = next(extract_a(mk))[0]
        yield Request(response.urljoin(url), callback=ls_parse)

        m = get_article(url)
        if m is None:
            continue

        m = make_article(m)
        m.update({k: extract_t(mk.xpath(v)) for k, v in xp.items()})

        img = mk.xpath('.//img/@src').extract_first()
        if img:
            m['image'] = img

        yield m


class MakerListSpider(JAVSpider):
    name = 'dmm.makers'

    start_urls = (
        'http://www.dmm.co.jp/digital/videoa/-/maker/=/keyword=a/',
        'http://www.dmm.co.jp/mono/dvd/-/maker/=/keyword=a/',
    )

    def parse(self, response):
        if get_type(response.url) == 'mono':
            mora = '(//td[@class="makerlist-box-t2" or @class="initial"])'
            xp = {
                'main': '//td[@class="w50"]',
                'name': './/a[@class="bold"]',
                'description': './/div[@class="maker-text"]',
            }

            subt = {
                'main': subt_main,
                'name': 'td/a',
                'description': '(td)[2]',
            }
            yield from makers(response, subt)
        else:
            mora = '(//ul[starts-with(@class,"d-mod")])[position()>1]'
            xp = {
                'main': '//div[@class="d-unit"]',
                'name': './/span[@class="d-ttllarge"]',
                'description': './/p',
            }

        yield from makers(response, xp)

        for url, t in extract_a(response.xpath(mora)):
            yield Request(response.urljoin(url))
