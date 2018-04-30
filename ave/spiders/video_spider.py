from scrapy import Request

from generics.spiders import JAVSpider
from generics.utils import extract_a, extract_t, get_key

from . import get_article, process_articles

JSON_FILENAME = 'videos/{studio}/{pid}.json'


class VideoSpider(JAVSpider):
    name = 'ave.video'

    def parse(self, response):

        pid = get_key(response.url, 'product_id')

        if not pid:
            print(response.url)
            return

        info = []
        articles = []

        main = response.xpath('//div[@class="main-subcontent-page"]/div[1]')

        for li in main.xpath('.//li'):
            links = tuple(extract_a(li))
            if links:
                for url, t in links:
                    if url.startswith('javascript:'):
                        continue
                    articles.append(get_article(url, t))
            else:
                label = extract_t(li.xpath('span'))
                if not label:
                    continue
                i = extract_t(li, p='text()[2]')
                if label[-1] == ':':
                    label = label[:-1]
                else:
                    label, i = label.split(': ')
                info.append((label, i))

        for ol in response.xpath('//div[@id="detailbox"]/ol'):
            t = extract_t(ol)
            if t:
                info.append(tuple(t.split(' |')[0].split(': ')))
            else:
                articles.append(get_article(*next((extract_a(ol)))))

        item = {
            'pid': int(pid),
            'url': response.url,
            'title': extract_t(response.xpath('//h2')),
            **{k: v for k, v in process_articles(articles)},
        }

        item['JSON_FILENAME'] = JSON_FILENAME.format(**item)

        yield item

        # for url, t in extract_a(response.xpath('//div[@id="mini-tabs"]')):
        #    yield Request(url, meta={'type': t})
