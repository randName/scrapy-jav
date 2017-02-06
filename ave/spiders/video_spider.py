from . import *


class VideoSpider(AVESpider):
    name = 'ave.video'
    base_url = 'video'

    def __init__(self, vids=None, **kwargs):
        super().__init__(**kwargs)

        if vids is not None:
            self.start_urls = tuple({'id': int(vid)} for vid in vids.split(','))

    def parse(self, response):
        item = response.meta.get('params', {})

        mutual = get_params('video', response.xpath('//div[@id="mini-tabs"]'))
        mutual_ids = set(v['id'] for v in related)
        mutual_ids.discard(item['id'])

        #for i in mutual_ids:
        #    yield VideoSpider.make_request({**item, 'id': i})

        maincontent = response.css('div.main-subcontent-page')
        detailbox = response.xpath('//div[@id="detailbox"]')

        #print(detailbox[0].xpath('ol').extract())

        articles = list(get_params('keyword', detailbox[1]))
        for k in (o2m+('actress',)):
            articles.extend(get_params(k, maincontent))

        for a in articles: yield a

        table = {k: v for k, v in self.get_table(maincontent, articles)}

        vid = {
            'cid': response.css('div.top-title::text').re_first('商品番号: (.*)'),
            'title': response.css('h2::text').extract_first(),
            'related': related_ids,
        }

        yield {**item, **vid, **table}

    def get_table(self, table, articles):
        t = table.xpath('.//li/text()')

        try:
            yield 'runtime', int(t.re_first(r'(\d+) Min.'))
        except (TypeError, ValueError):
            pass

        dt = t.re(r'(\d+)/(\d+)/(\d+)')
        if dt:
            dt = (dt[2], dt[0], dt[1])
            yield 'date', date(*tuple(int(n) for n in dt))

        for article, l in groupby(articles, key=lambda x: x['article']):
            if article in m2m:
                a_id = set(a['id'] for a in l)
            else:
                a_id = next(l)['id']
            yield article, a_id
