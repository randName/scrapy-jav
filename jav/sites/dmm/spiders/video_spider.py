from jav.spiders import JAVSpider
from jav.utils import get_aux

from ..items import DMMVideoLoader

mutual_l = '/misc/-/mutual-link/ajax-index/=/cid={0}/service={1}/shop={2}/'

text_labels = {
    '品番': 'cid',
    '発売日': 'date',
    '商品発売日': 'date',
    '収録時間': 'runtime',
    '配信開始日': 'delivery_date',
}

article_labels = (
    'ジャンル',
    'シリーズ',
    'メーカー',
    'レーベル',
    '出演者',
    '監督',
)


class VideoSpider(JAVSpider):
    name = 'dmm.video'

    retry_xpath = '//h1'

    json_filename = '{shop}/videos/{date}/{cid}.json'

    def parse(self, response):
        v = DMMVideoLoader(response=response)
        v.add_value('url', response.url.split('?'))
        v.add_value('shop', 'mono' if 'mono' in response.url else 'digital')

        v.add_xpath('title', '//h1/text()')
        v.add_xpath('cover', '//img[@class="tdmm"]/../@href')
        v.add_xpath('description', '//div[@class="mg-b20 lh4"]//text()')
        v.add_xpath('gallery', '//a[starts-with(@id,"sample-image")]/img/@src')

        for row in response.xpath('//td[@class="nw"]'):
            label = row.xpath('text()').extract_first()[:-1]
            r = v.nested(selector=row.xpath('following-sibling::td[1]'))

            if label in article_labels:
                r.add_xpath('articles', '(span|.)/a/@href')
            elif label in text_labels:
                r.add_xpath(text_labels[label], 'text()')

        m_l = response.xpath('//script[contains(.,"#mutual-link")]/text()')
        if m_l:
            m_l = response.urljoin(mutual_l.format(*m_l.re(r":\s*'(.*)',")))
            v.nested(selector=get_aux(m_l)).add_xpath('related', '//a/@href')

        a_p = response.xpath('//script[contains(.,"#a_performer")]/text()')
        if a_p:
            a_p = response.urljoin(a_p.re_first(r"url: '(.*)',"))
            v.nested(selector=get_aux(a_p)).add_xpath('articles', '//a/@href')

        item = v.load_item()
        yield item
