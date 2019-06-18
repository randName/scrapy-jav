from jav.utils import get_aux
from jav.items import JAVLoader

from .constants import MUTUALS


text_labels = {
    '品番': 'cid',
    '発売日': 'date',
    '商品発売日': 'date',
    '収録時間': 'runtime',
    '配信開始日': 'delivery_date',
}

xpaths = {
    'title': '//h1/text()',
    'image': '//img[@class="tdmm"]/../@href',
    'text': '//div[@class="mg-b20 lh4"]//text()',
    'gallery': '//a[@name="sample-image"]/img/@src',
    'related': '//div[@class="area-edition"]//a/@href',
    'articles': (
        '//span[@id="performer"]/a/@href',
        '//table[@class="mg-b20"]/tr/td/a/@href',
    ),
}


def parse_video(response):
    v = JAVLoader(response=response, xpaths=xpaths)

    for row in response.xpath('//td[@class="nw"]/..'):
        label, *vals = row.xpath('td/text()').getall()
        if not vals:
            continue
        label = text_labels.get(label[:-1])

        if label:
            v.add_value(label, vals[0].strip())

    m_l = response.xpath('//script[contains(.,"#mutual-link")]/text()')
    if m_l:
        m_l = response.urljoin(MUTUALS.format(*m_l.re(r":\s*'(.*)',")))
        v.nested(selector=get_aux(m_l)).add_xpath('related', '//a/@href')

    a_p = response.xpath('//script[contains(.,"#a_performer")]/text()')
    if a_p:
        a_p = response.urljoin(a_p.re_first(r"url: '(.*)',"))
        v.nested(selector=get_aux(a_p)).add_xpath('articles', '//a/@href')

    return v.load_item()
