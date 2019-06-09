from jav.spiders import JAVSpider
from jav.spiders.list_spider import UrlListSpider

from ..video import parse_video
from ..constants import PAGEN, DATE_URLS

tmb_xpath = '//p[@class="tmb"]/a'
monocal_xpath = '//td[@class="title-monocal"]'


class VideoSpider(JAVSpider):
    name = 'dmm.video'

    retry_xpath = '//h1'

    def export_items(self, response):
        yield parse_video(response)


class VideoListSpider(UrlListSpider):
    name = 'dmm.video.list'

    link_xp = tmb_xpath
    pagination_xpath = PAGEN

    start_urls = (
        'http://www.dmm.co.jp/digital/videoa/-/list/=/sort=release_date/',
        'http://www.dmm.co.jp/mono/dvd/-/list/=/sort=date/',
    )

    def export_items(self, response):
        yield parse_video(response)

    def get_list(self, response):
        for l in self.links(response, self.link_xp):
            yield l.split('?')[0]


class VideoDateSpider(VideoListSpider):
    name = 'dmm.video.date'

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

            yield self.make_request(DATE_URLS[0].format(d, last))

            while d <= last:
                yield self.make_request(DATE_URLS[1].format(d))
                d += one_day
        else:
            for url in DATE_URLS:
                yield self.make_request(url.format(d, d))
