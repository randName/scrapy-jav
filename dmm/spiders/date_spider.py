from datetime import datetime, timedelta

from scrapy import Request
from .list_spider import ListSpider

DMM_DOMAIN = 'http://www.dmm.co.jp'
DATE_MIN = datetime(2001, 3, 1)
ONE_DAY = timedelta(days=1)

link_xp = '//td[@class="title-monocal"]/a/@href'

date_urls = {
    'digital': 'digital/videoa/-/delivery-list/=/delivery_date={0:%Y-%m-%d}',
    'mono': 'mono/dvd/-/calendar/=/year={0:%Y}/month={0:%m}/day={0:%d}-{0:%d}'
}


class DateSpider(ListSpider):
    name = 'dmm.date'

    def start_requests(self):
        try:
            d = datetime.strptime(self.date, '%Y-%m-%d')
        except (AttributeError, ValueError):
            d = datetime.now()

        try:
            n = int(self.n)
        except (AttributeError, ValueError):
            n = 1

        for i in range(n):
            for shop, url in date_urls.items():
                yield Request(url='%s/%s' % (DMM_DOMAIN, url.format(d)))
            d -= ONE_DAY

    def export_item(self, response):
        if 'mono' in response.url:
            for url in response.xpath(link_xp).extract():
                yield {'url': DMM_DOMAIN + url}
        else:
            yield from super().export_item(response)
