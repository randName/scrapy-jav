from jav.spiders import JAVSpider

from ..video import parse_video
from ..constants import PAGEN, DOMAIN

tmb_xpath = '//p[@class="tmb"]'
monocal_xpath = '//td[@class="title-monocal"]'

date_urls = {
    'digital': 'digital/videoa/-/delivery-list/=/delivery_date={0:%Y-%m-%d}',
    'mono': 'mono/dvd/-/calendar/=/year={0:%Y}/month={0:%m}/day={0:%d}-{1:%d}'
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

    def parse_item(self, response):
        if response.meta.get('deep'):
            response.meta['export'] = (parse_video(response),)
            return ()

        urls = (l.split('?')[0] for l in self.links(response, self.link_xp))

        if self.deep:
            for url in urls:
                yield response.follow(url, meta={'deep': True})
        else:
            for url in urls:
                yield {'url': url}


class DateSpider(ListSpider):
    name = 'dmm.date'

    link_xp = '(%s|%s)' % (tmb_xpath, monocal_xpath)

    def __init__(self, date='', **kw):
        super().__init__(**kw)

        self.start, self.month = self.get_date(date)

    def get_date(self, d):
        from datetime import datetime
        try:
            return datetime.strptime(d, '%Y-%m-%d'), False
        except ValueError:
            try:
                return datetime.strptime(d, '%Y-%m'), True
            except ValueError:
                pass

        return datetime.now(), False

    def start_requests(self):
        d = self.start

        if self.month:
            from datetime import timedelta
            from calendar import monthrange

            one_day = timedelta(days=1)
            last_day = monthrange(d.year, d.month)[1]
            last = d.replace(day=last_day)

            url = date_urls['mono'].format(d, last)
            yield self.make_request('%s/%s' % (DOMAIN, url))

            url = date_urls['digital']
            while d <= last:
                yield self.make_request('%s/%s' % (DOMAIN, url.format(d)))
                d += one_day
        else:
            for url in date_urls.values():
                yield self.make_request('%s/%s' % (DOMAIN, url.format(d, d)))
