from jav.spiders import JAVSpider
from jav.utils import extract_t, extract_a

from ..article import get_article

subt_main = '(//table[contains(@class,"list-table")]//tr)[position()>1]'

mora = {
    'mono': '(//td[@class="makerlist-box-t2" or @class="initial"])',
    'digital': '(//ul[starts-with(@class,"d-mod")])[position()>1]'
}


class MakerSpider(JAVSpider):
    name = 'dmm.maker'

    start_urls = (
        'http://www.dmm.co.jp/digital/videoa/-/maker/=/keyword=a/',
        'http://www.dmm.co.jp/mono/dvd/-/maker/=/keyword=a/',
    )

    def makers(self, response, xp, genre=None):
        for mk in response.xpath(xp.pop('main')):
            url = next(extract_a(mk))[0]

            m = get_article(url)
            if m is None:
                continue

            m['url'] = response.urljoin(url)

            if genre is not None:
                m['genre'] = set((genre['id'],))
                yield m
                continue

            m.update({k: extract_t(mk.xpath(v)) for k, v in xp.items()})

            img = mk.xpath('.//img/@src').extract_first()
            if img:
                m['image'] = img

            yield m

    def parse_item(self, response):
        yield from super().parse_item(response)
        xp = mora['mono'] if 'mono' in response.url else mora['digital']
        yield from self.links(response, xp, follow=True)

    def export_items(self, response):
        if 'mono' in response.url:
            xp = {
                'main': '//td[@class="w50"]',
                'name': './/a[@class="bold"]',
                'description': './/div[@class="maker-text"]',
            }

            yield from self.makers(response, {
                'main': subt_main,
                'name': 'td/a',
                'description': '(td)[2]',
            })
        else:
            xp = {
                'main': '//div[@class="d-unit"]',
                'name': './/span[@class="d-ttllarge"]',
                'description': './/p',
            }

        yield from self.makers(response, xp, response.meta.get('genre'))


class MakerGenreSpider(MakerSpider):
    name = 'dmm.maker.genre'

    start_urls = (
        'http://www.dmm.co.jp/digital/videoa/-/maker/=/article=keyword/',
    )

    def parse_item(self, response):
        if response.meta.get('genre'):
            response.meta['export'] = self.export_items(response)
            return ()

        for section in response.xpath('//div[@class="d-sect"]')[2:-1]:
            for url in section.xpath('.//a/@href').extract():
                yield response.follow(url, meta={'genre': get_article(url)})
