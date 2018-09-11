from generics.utils import extract_t, extract_a
from . import ArticleSpider

subt_main = '(//table[contains(@class,"list-table")]//tr)[position()>1]'


class MakerSpider(ArticleSpider):
    name = 'dmm.maker'

    start_urls = (
        'http://www.dmm.co.jp/digital/videoa/-/maker/=/keyword=a/',
        'http://www.dmm.co.jp/mono/dvd/-/maker/=/keyword=a/',
    )

    def makers(self, response, xp, genre=None):
        for mk in response.xpath(xp.pop('main')):
            url = next(extract_a(mk))[0]

            m = self.get_article(url)
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

            yield m

    def export_item(self, response):
        if 'mono' in response.url:
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
            yield from self.makers(response, subt)
        else:
            mora = '(//ul[starts-with(@class,"d-mod")])[position()>1]'
            xp = {
                'main': '//div[@class="d-unit"]',
                'name': './/span[@class="d-ttllarge"]',
                'description': './/p',
            }

        g = response.meta.get('genre')
        yield from self.makers(response, xp, g)
        if g:
            return

        yield from self.links(response, mora)


class MakerGenreSpider(MakerSpider):
    name = 'dmm.maker.genre'

    start_urls = (
        'http://www.dmm.co.jp/digital/videoa/-/maker/=/article=keyword/',
    )

    def export_item(self, response):
        exp = super().export_item
        for section in response.xpath('//div[@class="d-sect"]')[2:-1]:
            sname = extract_t(section.xpath('p'))
            for url, t in extract_a(section):
                g = {'genre': self.get_article(url, category=sname)}
                yield response.follow(url, meta=g, callback=exp)
