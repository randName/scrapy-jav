from jav.spiders import JAVSpider

from ..constants import AIUEO

alias_re = r'(.+?)(?:（(.+?)）)?$'
PAGEN = '//td[@class="header"]/following-sibling::td'


def get_article(url):
    try:
        aid = int(url[:-1].split('=')[2])
    except (IndexError, ValueError):
        return None

    return {
        'id': aid,
        'article': 'actress'
    }


def details(table):
    for row in table.xpath('tr'):
        label, info = row.xpath('td/text()').getall()
        if info != '----':
            yield label[:-1], info


def parse_actress(response):
    tables = response.xpath('//table')

    if not response.meta.get('page'):
        actress = response.meta.get('item') or get_article(response.url)
        actress.update(details(tables[6]))
        yield actress

    for row in tables[-2].xpath('tr'):
        url, *works = row.xpath('td/a/@href').getall()
        yield {'url': url, 'related': works}


def parse_table(response):
    for row in response.xpath('//tr[@class="list"]'):
        url = row.xpath('td/a/@href').get()

        a = get_article(url)
        if a is None:
            continue

        image = row.xpath('td/a/img/@src').get()
        a['name'], alias = row.xpath('td[2]/a/text()').re(alias_re)
        a['kana'], alias_kana = row.xpath('td[3]/text()').re(alias_re)
        a['url'] = url

        if image:
            a['image'] = image

        if alias:
            a['alias'] = alias

        if alias_kana:
            a['alias_kana'] = alias_kana

        yield a


class ActressSpider(JAVSpider):
    name = 'dmm.actress'

    retry_xpath = '//h1'

    pagination_xpath = PAGEN

    def export_items(self, response):
        yield from parse_actress(response)


class ActressListSpider(JAVSpider):
    name = 'dmm.actress.list'

    deep = False

    start_urls = (
        'http://actress.dmm.co.jp/-/top/',
    )

    pagination_xpath = PAGEN

    def parse_item(self, response):
        if response.meta.get('item'):
            response.meta['export'] = parse_actress(response)
            return ()

        if not response.meta.get('_'):
            yield from self.links(response, AIUEO, follow=True, meta={'_': 1})

        actresses = parse_table(response)

        if self.deep:
            for a in actresses:
                yield response.follow(a['url'], meta={'item': a, '_': 1})
        else:
            response.meta['export'] = actresses
