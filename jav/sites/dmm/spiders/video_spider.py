from jav.spiders import JAVSpider

from ..video import parse_video
from ..constants import PAGEN, DOMAIN

tmb_xpath = '//p[@class="tmb"]'
monocal_xpath = '//td[@class="title-monocal"]'

date_urls = {
    'digital': 'digital/videoa/-/delivery-list/=/delivery_date={0:%Y-%m-%d}',
    'mono': 'mono/dvd/-/calendar/=/year={0:%Y}/month={0:%m}/day={0:%d}-{0:%d}'
}


class VideoSpider(JAVSpider):
    name = 'dmm.video'

    retry_xpath = '//h1'

    def export_items(self, response):
        yield parse_video(response)


class ListSpider(JAVSpider):
    name = 'dmm.list'

    link_xp = tmb_xpath
    pagination_xpath = PAGEN

    start_urls = (
        'http://www.dmm.co.jp/digital/videoa/-/list/=/sort=release_date/',
        'http://www.dmm.co.jp/mono/dvd/-/list/=/sort=date/',
    )

    def __init__(self, deep=False):
        self.deep = deep

    def parse_item(self, response):
        urls = (l.split('?')[0] for l in self.links(response, self.link_xp))

        if self.deep:
            for url in urls:
                yield response.follow(url, meta={'deep': True})
        else:
            for url in urls:
                yield {'url': url}

    def export_items(self, response):
        if response.meta.get('deep'):
            yield parse_video(response)


class DateSpider(ListSpider):
    name = 'dmm.date'

    link_xp = '(%s|%s)' % (tmb_xpath, monocal_xpath)

    def __init__(self, date='', n=1, **kw):
        super().__init__(**kw)
        
        from datetime import datetime
        try:
            d = datetime.strptime(date, '%Y-%m-%d')
        except (AttributeError, ValueError):
            d = datetime.now()

        try:
            n = int(n)
        except (AttributeError, ValueError):
            n = 1

        self.start = d
        self.days = n

    def start_requests(self):
        d = self.start

        from datetime import timedelta
        one_day = timedelta(days=1)

        for i in range(self.days):
            for url in date_urls.values():
                yield self.make_request('%s/%s' % (DOMAIN, url.format(d)))
            d -= one_day
