from datetime import datetime, timedelta
from humanfriendly import parse_size
from scrapy.exceptions import CloseSpider
from . import *


class ForumSpider(THZSpider):
    name = 'thz.forum'
    base_url = 'forum'

    custom_settings = {
        'ITEM_PIPELINES': {
            'thz.pipelines.DatabasePipeline': 300,
        },
    }

    def __init__(self, **kwargs):
        if 'fid' not in kwargs:
            kwargs['fid'] = 220
        if 'page' not in kwargs:
            kwargs['page'] = 1
        if 'maxp' not in kwargs:
            kwargs['maxp'] = 15
        if 'maxid' not in kwargs:
            kwargs['maxid'] = 1030000

        self.start_urls = kwargs,

    def parse(self, response):
        p = response.meta.get('params')

        for t in response.xpath('//tbody[contains(@id,"normalthread")]'):
            l = t.xpath('.//a[@class="s xst"]')
            thread = parse_url('thread', l.xpath('@href').extract_first())

            if int(thread['tid']) < int(p['maxid']):
                print(thread['tid'])
                raise CloseSpider("Reached old")

            thread['page'] = 1
            thread['_'] = 1
            #thread['title'] = l.xpath('text()').extract_first()
            yield ThreadSpider.make_request(thread)
            #yield thread

        if p.get('maxp', 0) > 1:
            p['page'] += 1
            p['maxp'] -= 1
            yield self.make_request(p)


class ThreadSpider(THZSpider):
    name = 'thz.thread'
    base_url = 'thread'

    def __init__(self, ids=None, **kwargs):
        p = { 'page': 1, '_': 1 }
        if ids is not None:
            self.start_urls = tuple({**p, 'tid': int(i)} for i in ids.split(','))

    def parse(self, response):

        def get_details(x):
            store = { '片名': 'title', '容量': 'filesize', '格式': 'filetype', '品番': 'cid' }
            #配信開始日 商品発売日 収録時間 出演者 監督 シリーズ メーカー レーベル ジャンル
            for t in x:
                i = t.strip().replace('\xa0','').split('：', 1)
                if i[0] in store:
                    yield store[i[0]], i[1].strip()

        def get_date(p):
            fmt = '%Y-%m-%d %H:%M'
            for d in p.xpath('//span/@title').extract():
                try:
                    return datetime.strptime(d, fmt)
                except ValueError:
                    pass
            for d in p.css('p.y::text').extract():
                try:
                    return datetime.strptime(d, fmt)
                except ValueError as v:
                    ulr = len(v.args[0].partition('unconverted data remains: ')[2])
                    if ulr:
                        return datetime.strptime(d[:-ulr], fmt)

        params = response.meta.get('params')
        torrent = response.xpath('//a[contains(@id,"aid")]').xpath('(text()|@href)').extract()

        p = response.xpath('//td[contains(@id,"postmessage")]')[0]
        postdate = get_date(p)

        img = p.xpath('.//img').xpath('(@id|@file)').extract()
        details = {k: v for k, v in get_details(p.xpath('text()').extract())}

        try:
            yield {
                'id': params['tid'],
                'cid': details['cid'],
                'date': postdate,
                'title': details['title'],
                'images': tuple(zip(img[::2], img[1::2])),
                'torrent': {
                    'aid': torrent[0].split('=')[1],
                    'name': torrent[1],
                    'size': int(parse_size(details['filesize'])/1000),
                }
            }

        except KeyError:
            pass
