from generics.spiders import JAVSpider
from generics.utils import extract_t, extract_a

from . import get_type
from . import get_article, article_json

subt_main = '(//table[contains(@class,"list-table")]//tr)[position()>1]'


def makers(response, xp, genre=None):
    for mk in response.xpath(xp.pop('main')):
        url = next(extract_a(mk))[0]

        m = get_article(url)
        if m is None:
            continue

        if genre is not None:
            m['genre'] = set((genre['id'],))
            yield m
            continue

        m.update({k: extract_t(mk.xpath(v)) for k, v in xp.items()})

        img = mk.xpath('.//img/@src').extract_first()
        if img:
            m['image'] = img

        article_json(m)
        yield m


class MakerSpider(JAVSpider):
    name = 'dmm.maker'

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

        g = response.meta.get('genre')
        yield from makers(response, xp, g)
        if g:
            return

        for url, t in extract_a(response.xpath(mora)):
            yield response.follow(url)


m_parse = MakerSpider().parse


class MakerGenreSpider(JAVSpider):
    name = 'dmm.maker.genre'

    start_urls = (
        'http://www.dmm.co.jp/digital/videoa/-/maker/=/article=keyword/',
    )

    def parse(self, response):
        for section in response.xpath('//div[@class="d-sect"]')[2:-1]:
            sname = extract_t(section.xpath('p'))
            for url, t in extract_a(section):
                g = get_article(url)
                g['category'] = sname
                yield response.follow(url, meta={'genre': g}, callback=m_parse)
