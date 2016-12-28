import scrapy
import re

from urllib.parse import urlsplit, urljoin
from os.path import dirname, basename
from . import *


class VideoSpider(scrapy.Spider):
    name = 'videos'

    rt = re.compile(r'(\d+)分')
    rowtag = { '売日': 'date', '品番': 'cid' }
    art_id = re.compile(r'article=(\w+)/id=(\d+)')

    def __init__(s, *args, **kwargs):
        super().__init__(*args, **kwargs)

        try:
            r = int(kwargs['realm']),
        except (KeyError, ValueError):
            r = None

        try:
            p = { a: kwargs[a] for a in ('article', 'id') }
        except KeyError:
            p = {}

        p['sort'] = kwargs['sort'] if 'sort' in kwargs else 'release_date'
        s.start_urls = realm_urls('-/list/=/%s' % urlparams(**p), realm=r)

    def article_links(s, links):
        articles = { 'links': [], 'id': [] }
        i = {}
        for l in links:
            try:
                a = s.art_id.search(l).groups()
                if 'article' not in i:
                    i['article'] = a[0]
                i['id'] = int(a[1])
                articles['links'].append((l, i))
                articles['id'].append(i['id'])
            except (TypeError, AttributeError):
                pass
        try:
            articles['article'] = i['article']
        except KeyError:
            pass
        return articles

    def parse(s, r):
        yield from pagelist(r.css('div.list-boxpagenation'), callback=s.parse)
        yield from pagelist(r, selector='p.tmb', callback=s.parse_video)

    def parse_video(s, r):
        vid = {
            'url': r.url,
            'title': r.css('h1::text').extract_first(),
            'rating': r.css("div.d-review__points strong::text").extract(),
        }

        pkg = urlsplit(r.css('img.tdmm::attr(src)').extract_first()).path
        vid['pkg'] = basename(dirname(pkg))

        samples = r.css('a[id*=sample-image] %s' % isrc).extract()
        if samples:
            vid['samples'] = len(samples)
            vid['samples_path'] = dirname(urlsplit(samples[0]).path)

        d = r.css("div.mg-b20.lh4")
        desc = d.css("p.mg-b20::text").extract_first()
        if not desc:
            desc = d.css("::text").extract_first()
        vid['description'] = desc.strip('\n')

        for row in r.css('div.page-detail table table tr'):
            a = s.article_links(row.css(href).extract())
            for i in a['links']:
                u = urljoin(r.url, i[0])
                rq = scrapy.Request(u, callback=s.parse_article)
                rq.meta['item'] = i[1]
                yield rq

            if a['id']:
                k = a['article']
                vid[k] = a['id'] if k in ('actress', 'keyword') else a['id'][0]
                continue

            d = row.css('td::text').extract()
            try:
                vid[s.rowtag[d[0][-3:-1]]] = d[1].strip('\n')
                continue
            except (IndexError, KeyError):
                pass
            try:
                vid['runtime'] = int(s.rt.match(d[1]).group(1))
            except (IndexError, AttributeError):
                pass

        yield vid

    def parse_article(s, r):
        item = r.meta['item']
        span = r.css("p.headwithelem span::text").extract()
        item['name'] = ''.join(span[:2]).split('\xa0')[-1].strip('\n')
        yield item
