from scrapy import Request

from generics.spiders import JAVSpider
from generics.utils import extract_a, extract_t

from . import get_pid, get_article, make_article

JSON_FILENAME = '{type}/videos/{studio}/{pid}.json'

cover_xp = '//div[@class="top_sample"]//img/@src'
main_xp = '//div[@class="main-subcontent-page"]/div[1]//li'

info_box = {
    '主演女優': ('actress', tuple),
    '女優名': ('actress', tuple),
    'スタジオ': ('studio', next),
    'シリーズ': ('series', next),
    'カテゴリ一覧': ('keyword', tuple),
    'カテゴリー': ('keyword', tuple),
    '発売日': ('date', None),
    '収録時間': ('runtime', None),
}


def get_articles(links, urls=None, only_id=True):
    for url, t in extract_a(links):
        if url.startswith('javascript:'):
            continue

        a = get_article(url)
        if a is None:
            continue

        a['name'] = t

        if urls is not None:
            urls[url] = a

        yield a['id'] if only_id else (a[k] for k in ('article', 'id'))


class VideoSpider(JAVSpider):
    name = 'ave.video'

    def parse(self, response):
        p_type, pid = get_pid(response.url)

        if not pid:
            print(response.url)
            return

        desc = response.xpath('//div[@class="title2"]/following-sibling::p')
        if p_type == 'PPV':
            desc = response.xpath('//ul[@class="review"]/li[1]')

        item = {
            'pid': pid,
            'type': p_type,
            'url': response.url,
            'title': extract_t(response.xpath('//h2')),
            'description': extract_t(desc),
        }

        vid = extract_t(response.xpath('//div[@class="top-title"]'))
        item['vid'] = vid.split(': ')[1]

        for src in response.xpath(cover_xp).extract():
            if 'imgs.aventertainments' in src:
                item['cover'] = src
                break

        urls = {}

        for li in response.xpath(main_xp):
            info = extract_t(li.xpath('span') or li)
            try:
                info, parser = info_box[info[:-1]]
            except KeyError:
                continue

            if parser is None:
                item[info] = extract_t(li, p='text()[2]')
            else:
                try:
                    i = parser(get_articles(li, urls))
                except StopIteration:
                    i = None
                item[info] = i

        for details in response.xpath('//div[@id="detailbox"]'):
            info = extract_t(details.xpath('span'))
            try:
                info, parser = info_box[info[:-1]]
            except KeyError:
                continue

            if parser is None:
                pass
            else:
                try:
                    item[info] += parser(get_articles(details, urls))
                except StopIteration:
                    pass

        item['keyword'] = sorted(set(item.pop('keyword')))

        sample = response.xpath('//div[@class="TabbedPanels"]//img')
        if sample:
            item['sample_link'] = sample.xpath('@src').extract_first()

        th = response.css('ul.thumbs')
        if th:
            item['gallery'] = tuple(extract_t(ul, 'li/a/@href') for ul in th)

        mutual = response.xpath('//div[@id="mini-tabs"]')
        if mutual:
            item['mutual'] = sorted(i[0] for i in extract_a(mutual))

        for url, a in urls.items():
            a['type'] = p_type
            article = make_article(a)
            if article:
                yield article

        item['JSON_FILENAME'] = JSON_FILENAME.format(**item)

        yield item
