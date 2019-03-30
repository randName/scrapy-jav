from jav.spiders import JAVSpider

from ..article import get_article


def mora_xp(url):
    if 'mono' in url:
        return '(//td[@class="makerlist-box-t2" or @class="initial"])'
    else:
        return '//ul[@class="d-modtab" or @class="d-modsort-la"]'


class MakerSpider(JAVSpider):
    name = 'dmm.maker'

    start_urls = (
        'http://www.dmm.co.jp/digital/videoa/-/maker/=/keyword=nn/',
        'http://www.dmm.co.jp/mono/dvd/-/maker/=/keyword=nn/',
    )

    def makers(self, response, xp, genre=None):
        for mk in response.xpath(xp.pop('main')):
            url = mk.xpath('.//a/@href').get('')

            m = get_article(url)
            if m is None:
                continue

            m['url'] = response.urljoin(url)

            if genre is not None:
                m['genre'] = set((genre['id'],))
                yield m
                continue

            m.update({k: mk.xpath(v).get('').strip() for k, v in xp.items()})

            yield m

    def parse_item(self, response):
        yield from super().parse_item(response)
        yield from self.links(response, mora_xp(response.url), follow=True)

    def export_items(self, response):
        if 'mono' in response.url:
            xp = {
                'main': '//td[@class="w50"]',
                'name': 'div/a/text()',
                'image': 'a/img/@src',
                'text': 'div[@class="maker-text"]/text()',
            }

            yield from self.makers(response, {
                'main': '//table[@class="list-table mg-t12"]/tr',
                'name': 'td/a/text()',
                'text': 'td[2]/text()',
            })
        else:
            xp = {
                'main': '//div[@class="d-unit"]',
                'name': 'div/a/span[@class="d-ttllarge"]/text()',
                'image': 'div/a//img/@src',
                'text': 'div/div/p/text()',
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
            for url in section.xpath('.//a/@href').getall():
                yield response.follow(url, meta={'genre': get_article(url)})
