from jav.spiders import JAVSpider
from jav.utils import extract_a, extract_t

from ..items import AVEVideoLoader
from . import parse_ave_url

xp = '//div[@id="detailbox"]|//div[@class="main-subcontent-page"]/div[1]//li'
vid_re = r'.*: (.*)'
cov_re = r".*url\('(.*)'\).*"

text_labels = {
    '発売日': 'date',
    '配信日': 'date',
    '収録時間': 'runtime',
}

article_labels = (
    'スタジオ',
    'シリーズ',
    '女優名',
    '主演女優',
    'カテゴリー',
    'カテゴリ一覧',
)


class VideoSpider(JAVSpider):
    name = 'ave.video'

    retry_xpath = '//h2'

    json_filename = '{shop}/videos/{pid}.json'

    def parse(self, response):
        a = parse_ave_url(response.url)

        if a.get('base') != 'video':
            print(response.url)
            return

        v = AVEVideoLoader(response=response)
        v.add_value('url', response.url)
        v.add_value('shop', a['shop'])
        v.add_value('pid', a['id'])

        v.add_xpath('title', '//h3/text()')
        v.add_xpath('vid', '//div[@class="top-title"]/text()', re=vid_re)
        v.add_xpath('cover', '//div[@class="top_sample"]/style', re=cov_re)

        v.add_xpath('gallery', '//a[@href="#title"]/img/@src')
        v.add_xpath('gallery', '//ul[@class="thumbs"]//a/@href')
        v.add_xpath('related', '//div[@id="mini-tabs"]//a/@href')
        v.add_xpath('description', '//div[@class="border"]/p/text()')
        v.add_xpath('description', '//ul[@class="review"]/li[1]/text()')

        for detail in response.xpath(xp):
            label = detail.xpath('string(.|span)').extract_first()
            try:
                label, text = label.strip().split(':')
            except ValueError:
                continue

            r = v.nested(selector=detail)
            if label in article_labels:
                r.add_xpath('articles', './/a/@href')
            elif label in text_labels:
                r.add_value(text_labels[label], text)

        item = v.load_item()
        yield item
