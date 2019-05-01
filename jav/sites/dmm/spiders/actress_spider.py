from jav.spiders import JAVSpider

from ..constants import AIUEO, PAGEN
from ..article import get_article, parse_article

name_re = r'(.+?)(?:[(（](.+?)[)）]?)?(?:（.+?）)?$'
table_pagen = '//td[@class="header"]/following-sibling::td/a'
works_xpath = '//td[@class="t_works1"]/../following-sibling::tr'


def get_actress(url):
    try:
        return {
            'article': 'actress',
            'id': int(url[:-1].split('=')[2]),
        }
    except (IndexError, ValueError):
        return None


def details(response):
    for row in response.xpath('//table[@class="w100"]//table/tr'):
        label, info = row.xpath('td/text()').getall()
        if info != '----':
            yield label[:-1], info


def parse_actress(response):
    init = response.meta.get(0)
    page = response.meta.get('page')

    if page and not init:
        for row in response.xpath(works_xpath):
            works = row.xpath('td/a/@href')
            if not works:
                continue
            url, *related = works.getall()
            yield {'url': url, 'related': related}
    elif init and not page:
        item = response.meta.get('article') or get_actress(response.url)
        item.update(details(response))
        yield item


def actresses(response):
    if 'actress.dmm' in response.url:
        parse_url = get_actress
        main_xp = '//tr[@class="list"]'
    else:
        parse_url = get_article
        main_xp = '//div[contains(@class,"act-box")]/ul/li/a'

    for act in response.xpath(main_xp):
        url = act.xpath('(td/a|.)/@href').get().split('sort')[0]

        a = parse_url(url)
        if a is None:
            continue

        image = act.xpath('(td/a|.)/img/@src').get()
        a['name'], alias = act.xpath('(td[2]/a|.)/text()').re(name_re)
        a['url'] = response.urljoin(url)

        if image:
            a['image'] = image

        if alias:
            a['alias'] = alias

        try:
            a['kana'], ak = act.xpath('(td[3]|span[1])/text()').re(name_re)
            if ak:
                a['alias_kana'] = ak
        except ValueError:
            pass

        yield a


class ActressSpider(JAVSpider):
    name = 'dmm.actress'

    deep = False

    start_urls = (
        'http://www.dmm.co.jp/digital/videoa/-/actress/=/keyword=nn/',
        'http://www.dmm.co.jp/mono/dvd/-/actress/=/keyword=nn/',
        'http://actress.dmm.co.jp/-/top/',
    )

    pagination_xpath = '(%s|%s)' % (PAGEN, table_pagen)

    def parse_item(self, response):
        page = response.meta.get('page')

        if not page and not response.meta.get(0):
            yield from self.links(response, AIUEO, follow=True, meta={0: 1})

        if response.meta.get('article'):
            if 'actress.dmm' in response.url:
                export = parse_actress(response)
            else:
                export = (parse_article(response),)
            response.meta['export'] = export

        elif self.deep:
            for a in actresses(response):
                yield response.follow(a['url'], meta={'article': a, 0: 1})

        elif page != 1:
            response.meta['export'] = actresses(response)
