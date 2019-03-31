from jav.utils import get_aux
from jav.items import JAVLoader, Video
from jav.items import URLField, StringField, ArticleField

from .article import save_article
from .constants import MUTUALS, RELATED, ARTICLE_LABELS

text_labels = {
    '品番': 'cid',
    '発売日': 'date',
    '商品発売日': 'date',
    '収録時間': 'runtime',
    '配信開始日': 'delivery_date',
}


class DMMVideo(Video):
    cid = StringField()
    date = StringField()
    runtime = StringField()
    articles = ArticleField(save_article)
    delivery_date = StringField()
    text = StringField()

    cover = URLField()
    gallery = URLField(multi=True)
    related = URLField(multi=True)


def parse_video(response):
    v = JAVLoader(item=DMMVideo(), response=response)

    v.add_xpath('title', '//h1/text()')
    v.add_xpath('cover', '//img[@class="tdmm"]/../@href')
    v.add_xpath('text', '//div[@class="mg-b20 lh4"]//text()')
    v.add_xpath('gallery', '//a[starts-with(@id,"sample-image")]/img/@src')
    v.add_xpath('related', '//div[@class="area-edition"]//a/@href')

    for row in response.xpath('//td[@class="nw"]'):
        label = row.xpath('text()').get()[:-1]
        r = v.nested(selector=row.xpath('following-sibling::td[1]'))

        if label in ARTICLE_LABELS:
            r.add_xpath('articles', '(span|.)/a/@href')
        elif label in text_labels:
            r.add_xpath(text_labels[label], 'text()')

    m_l = response.xpath('//script[contains(.,"#mutual-link")]/text()')
    if m_l:
        m_l = response.urljoin(MUTUALS.format(*m_l.re(r":\s*'(.*)',")))
        v.nested(selector=get_aux(m_l)).add_xpath('related', '//a/@href')

    a_p = response.xpath('//script[contains(.,"#a_performer")]/text()')
    if a_p:
        a_p = response.urljoin(a_p.re_first(r"url: '(.*)',"))
        v.nested(selector=get_aux(a_p)).add_xpath('articles', '//a/@href')

    return v.load_item()


def get_related_product(response):
    for fx in response.xpath('//div[@class="sect02-r"]/p/a/@onclick'):
        p = fx.re(r'\'([^\',]*)\'')
        ch = p[3] if len(p) > 3 else ''
        yield RELATED.format(p[0], p[1] or ch, p[2])


def parse_product(response):
    v = JAVLoader(item=DMMVideo(), response=response)

    v.add_xpath('title', '//h1[@id="title"]/text()')
    v.add_xpath('cover', '//a[@name="package-image"]/@href')
    v.add_xpath('text', '//div[@class="mg-b20 lh4"]/text()')
    v.add_xpath('gallery', '//a[@name="sample-image"]/img/@src')
    v.add_value('related', get_related_product(response))

    for row in response.xpath('//td[@class="nw"]'):
        label = row.xpath('text()').get().strip()[:-1]
        r = v.nested(selector=row.xpath('following-sibling::td[1]'))

        if label in text_labels:
            r.add_xpath(text_labels[label], 'text()')

    return v.load_item()
