from jav.items import JAVLoader, Video
from jav.items import URLField, StringField, ArticleField

from .article import save_article
from .constants import ARTICLE_LABELS

vid_re = r'.*: (.*)'
cov_re = r".*url\('(.*)'\).*"
xp = '//div[@class="main-subcontent-page"]/div[1]/ul/li'

text_labels = {
    '発売日': 'date',
    '配信日': 'date',
    '収録時間': 'runtime',
}


class AVEVideo(Video):
    vid = StringField()
    date = StringField()
    runtime = StringField()
    articles = ArticleField(save_article)
    text = StringField()

    cover = URLField()
    gallery = URLField(multi=True)
    related = URLField(multi=True)
    screenshot = URLField(multi=True)


def parse_video(response):
    v = JAVLoader(item=AVEVideo(), response=response)

    v.add_xpath('title', '//h3/text()')
    v.add_xpath('vid', '//div[@class="top-title"]/text()', re=vid_re)
    v.add_xpath('cover', '//div[@class="top_sample"]/style', re=cov_re)
    v.add_xpath('text', '//div[@class="border"]/p/text()')
    v.add_xpath('text', '//ul[@class="review"]/li[1]/text()')
    v.add_xpath('gallery', '//a[@href="#title"]/img/@src')
    v.add_xpath('gallery', '//ul[@class="thumbs"]//a/@href')
    v.add_xpath('related', '//div[@id="mini-tabs"]//a/@href')
    v.add_xpath('screenshot', '//ul[@class="thumbs noscript"]//a/@href')

    for detail in response.xpath(xp):
        label = detail.xpath('string(.|span)').get()
        try:
            label, text = label.strip().split(':')
        except ValueError:
            continue

        r = v.nested(selector=detail)
        if label in ARTICLE_LABELS:
            r.add_xpath('articles', './/a/@href')
        elif label in text_labels:
            r.add_value(text_labels[label], text)

    return v.load_item()
