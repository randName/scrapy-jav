from scrapy import Request

from generics.spiders import JAVSpider
from generics.utils import get_aux, extract_t, extract_a

from . import get_type, make_article, get_articles

JSON_FILENAME = '{type}/videos/{maker}/{cid}.json'

mutual_l = '/misc/-/mutual-link/ajax-index/=/cid={0}/service={1}/shop={2}/'
cover_xp = '//img[@class="tdmm"]/../@href'

info_box = {
    '発売日': ('date', None),
    '商品発売日': ('date', None),
    '配信開始日': ('date_del', None),
    '収録時間': ('runtime', None),
    'ジャンル': ('keyword', tuple),
    'シリーズ': ('series', next),
    'メーカー': ('maker', next),
    'レーベル': ('label', next),
    '出演者': ('performer', 'PERFORMER'),
    '監督': ('director', next),
    '品番': ('cid', None),
}


def get_performers(performers, urls):
    """Split performers into actress and histrion."""
    perf = ('actress', 'histrion')
    p = sorted(get_articles(performers, urls, only_id=False))
    return {k: tuple(i for a, i in p if a == k) for k in perf}


class VideoSpider(JAVSpider):
    name = 'dmm.video'

    def parse(self, response):
        v_type = get_type(response.url)

        desc = response.css('div.mg-b20.lh4')
        if v_type == 'mono':
            desc = desc.xpath('p')

        item = {
            'type': v_type,
            'url': response.url.split('?')[0],
            'title': extract_t(response.xpath('//h1')),
            'cover': response.xpath(cover_xp).extract_first(),
            'description': extract_t(desc),
        }

        urls = {}

        for row in response.xpath('//td[@class="nw"]/..'):
            info = extract_t(row.xpath('td'))[:-1]
            try:
                info, parser = info_box[info]
            except KeyError:
                continue

            if parser == 'PERFORMER':
                item.update(get_performers(row.xpath('td'), urls))
            elif parser is None:
                item[info] = extract_t(row.xpath('td[2]'))
            else:
                try:
                    i = parser(get_articles(row.xpath('td'), urls))
                except StopIteration:
                    i = None
                item[info] = i

        sample = response.xpath('//a[starts-with(@id,"sample-image")]/img')
        item['samples'] = len(sample)
        item['sample_link'] = sample.xpath('@src').extract_first()

        m_l = response.xpath('//script[contains(.,"#mutual-link")]/text()')
        if m_l:
            m_l = response.urljoin(mutual_l.format(*m_l.re(r":\s*'(.*)',")))
            item['mutual'] = sorted(i[0] for i in extract_a(get_aux(m_l)))

        a_p = response.xpath('//script[contains(.,"#a_performer")]/text()')
        if a_p:
            a_p = response.urljoin(a_p.re_first(r"url: '(.*)',"))
            item.update(get_performers(get_aux(a_p), urls))

        for url, a in urls.items():
            a['type'] = v_type
            yield make_article(a)

        try:
            item['JSON_FILENAME'] = JSON_FILENAME.format(**item)
        except KeyError:
            print(item)

        yield item
