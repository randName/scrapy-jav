# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.

import re
from scrapy import Spider, Request

realms = {
    '0': { 'service': 'digital', 'shop': 'videoa' },
    '1': { 'service': 'mono', 'shop': 'dvd' }
}

url_bases = {
    'video': '{service}/{shop}/-/detail/=/cid={cid}',
    'pic': '{service}/{realm}/{pkg}/{_pkg}{type}.jpg',
    'article': '{service}/{shop}/-/list/=/article={article}/id={id}',
    'related': 'misc/-/mutual-link/ajax-index/=/cid={cid}/service={service}/shop={shop}'
}

_re = {k: r'(?P<%s>\w+)'%k for k in ('service', 'shop', 'article', 'cid', 'pkg')}
_re['id'] = r'(?P<id>\d+)'
_re['realm'] = r'(video|movie/adult|\w+)'
_re['_pkg'] = '(?P=pkg)'
_re['type'] = '(?P<type>[a-z0-9-]+)'

matchers = {t: re.compile(url_bases[t].format(**_re)) for t in ('article','video','pic')}

href = 'a::attr(href)'
isrc = 'img::attr(src)'
pagediv = 'div.list-boxpagenation'

class DMMSpider(Spider):
    name = 'dmm'
    base_url = 'http://www.dmm.co.jp/'

    def __init__(self, realm=None, **kwargs):
        super().__init__(**kwargs)

        try:
            self.realm = realms[realm],
        except KeyError:
            self.realm = realms['0'], #realms.values()

        self.start_urls = ()

    def start_requests(self):
        for r in self.realm:
            for u in self.start_urls:
                p = {**r, **u}
                yield Request(self.base_url.format(**p), meta={'params': p})

    @classmethod
    def make_request(cls, params):
        if not params: return
        url = cls.base_url.format(**params)
        return Request(url, callback=cls().parse, meta={'params': params})

    @staticmethod
    def pagelist(links, selector='li'):
        return links.css('%s %s' % (selector, href)).extract()

    @staticmethod
    def get_params(matcher, links):
        for url in links:
            try:
                yield matchers[matcher].search(url).groupdict()
            except AttributeError:
                pass


class RelatedSpider(DMMSpider):
    name = 'dmm.related'
    base_url = DMMSpider.base_url + url_bases['related']

    def __init__(self, cids=None, **kwargs):
        super().__init__(**kwargs)

        if cids is not None:
            self.start_urls = tuple({'cid': cid} for cid in cids.split(','))

    def parse(self, response):
        item = response.meta.get('params', {})
        related = tuple(self.get_params('video', response.css(href).extract()))
        yield {'related': related + (item,)}


class ArticleSpider(DMMSpider):
    name = 'dmm.article'
    base_url = DMMSpider.base_url + url_bases['article']

    def __init__(self, article=None, ids=None, **kwargs):
        super().__init__(**kwargs)

        if article is not None:
            if ids is None: return
            ids = ids.split(',')
            self.start_urls = tuple({'article': article, 'id': i} for i in ids)

    def parse(self, response):
        item = response.meta.get('params', {})

        if 'name' not in item:
            span = response.css('p.headwithelem span::text').extract()
            item['name'] = ''.join(span[:2]).split('\xa0')[-1].strip('\n')

        ct = response.css(pagediv+' p::text').extract_first()

        try:
            item['count'] = int(re.match(r'(\d+)', ct.replace(',','')).group(1))
        except (ValueError, AttributeError):
            item['count'] = 0

        yield item


class VideoSpider(DMMSpider):
    name = 'dmm.video'
    base_url = DMMSpider.base_url + url_bases['video']
    runtime_re = re.compile(r'(\d+)分')

    def __init__(self, cids=None, **kwargs):
        super().__init__(**kwargs)

        if cids is not None:
            self.start_urls = tuple({'cid': cid} for cid in cids.split(','))

    def parse(self, response):
        item = response.meta.get('params', {})
        table_css = response.css('div.page-detail table table tr')
        table = { k: v for k, v in self.get_table(table_css) }
        pic_css = response.css('img.tdmm::attr(src)').extract()
        pic = next(self.get_params('pic', pic_css))

        vid = {
            'pkg': pic['pkg'],
            'title': response.css('h1::text').extract_first(),
            'description': self.get_description(response.css('div.mg-b20.lh4')),
            'rating': response.css('div.d-review__points strong::text').extract(),
        }

        samples = response.css('a[id*=sample-image] %s' % isrc).extract()
        vid['samples'] = len(samples)
        #vid['samples_path'] = self.urlparams('pic', samples[0])

        yield RelatedSpider.make_request(item)

        for a in table['requests']:
            yield ArticleSpider.make_request({**item,**a})
        del table['requests']

        yield {**item, **vid, **table}

    @staticmethod
    def get_description(d):
        desc = d.css('p.mg-b20::text').extract_first()
        if not desc:
            desc = d.css('::text').extract_first()
        return desc.strip('\n')

    @staticmethod
    def get_table(table):
        m2m = ('actress', 'keyword', 'histrion')
        requests = []

        for row in table:
            articles = tuple(DMMSpider.get_params('article', row.css(href).extract()))
            requests.extend(articles)

            if articles:
                a = articles[0]
                a_id = int(a['id'])
                if a['article'] in m2m:
                    a_id = tuple(int(a['id']) for a in articles)
                yield a['article'], a_id
                continue

            d = row.css('td::text').extract()
            try:
                yield 'runtime', int(VideoSpider.runtime_re.match(d[1]).group(1))
            except (IndexError, AttributeError):
                pass
            try:
                if d[0][-3:-1] == '売日':
                    date_str = d[1].strip('\n') if '/' in d[1] else ''
                    yield 'date', date_str
            except (IndexError, KeyError):
                pass

        yield 'requests', requests
