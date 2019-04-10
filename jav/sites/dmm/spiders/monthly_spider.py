from jav.spiders import JAVSpider

from ..constants import PAGEN
from ..article import get_article

side_xp = '//div[@id="monthly-localnav"]/ul/li/a/@href'
list_xp = '//ul[@id="list"]/li/div/a/@href'
maker_xp = '//td[@class="header"]/a/@href'


class MonthlySpider(JAVSpider):
    name = 'dmm.monthly'

    start_urls = ('https://www.dmm.co.jp/monthly/',)

    pagination_xpath = PAGEN

    def parse_item(self, response):
        stage = response.meta.get(0)
        page = response.meta.get('page')

        if stage is None and page is None:
            for url in response.xpath(side_xp).getall():
                yield response.follow(url, meta={0: 0})
        elif stage == 0:
            date_list = None
            for dgm in response.xpath('//h1[@class="dgm-ttl"]/a'):
                url, t = dgm.xpath('@href|text()').getall()
                if t == 'AVメーカー一覧へ':
                    yield response.follow(url, meta={0: 1})
                    break
                if 'sort=date' in url:
                    date_list = url
            else:
                if date_list:
                    yield response.follow(date_list, meta={0: 2})
        elif stage == 1:
            for url in response.xpath(maker_xp).getall():
                m = get_article(url)
                if not m:
                    continue
                yield response.follow(url, meta={0: 2, 'article': m})
        elif page != 1:
            response.meta['export'] = self.export_items(response)

    def export_items(self, response):
        for url in response.xpath(list_xp).getall():
            yield {'url': url}
