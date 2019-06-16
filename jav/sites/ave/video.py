from jav.items import JAVLoader

from .article import save_article
from .constants import ARTICLE_LABELS

vid_re = r'.*: (.*)'
cov_re = r".*url\('(.*)'\).*"
info_xp = '//div[@class="main-subcontent-page"]/div[1]/ul/li'

text_labels = {
    '発売日': 'date',
    '配信日': 'date',
    '収録時間': 'runtime',
}

xpaths = {
    'title': '//h2/text()',
    'related': '//div[@id="mini-tabs"]//a/@href',
    'text': (
        '//div[@class="border"]/p/text()',
        '//ul[@class="review"]/li[1]/text()',
    ),
    'gallery': (
        '//a[@href="#title"]/img/@src',
        '//ul[contains(@class,"thumbs")]/li/a/@href',
    ),
    'articles': '%s/a/@href' % info_xp,
}


def get_info(li):
    for text in li.xpath('(.|span)/text()').getall():
        t = text.strip()
        if not t:
            continue
        yield t


def parse_video(response):
    v = JAVLoader(response=response, xpaths=xpaths)
    v.add_xpath('vid', '//div[@class="top-title"]/text()', re=vid_re)
    v.add_xpath('image', '//div[@class="top_sample"]/style', re=cov_re)

    for li in response.xpath(info_xp):
        info = tuple(get_info(li))
        if not info:
            continue
        label = text_labels.get(info[0][:-1])
        if label:
            v.add_value(label, info[1])

    return v.load_item()
