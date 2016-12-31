from scrapy import Spider, Request
from .article_spider import ArticleSpider
from . import *


class MakerSpider(scrapy.Spider):
    name = 'makers'
    ars = ArticleSpider()
    start_urls = realm_urls('-/maker/=/keyword=a')

    def parse(s, r):
        sel = {
            'link': href,
            'pic' : isrc,
        }

        if get_realm(r.url) == 0:
            for li in ('ul.d-modsort-la', 'ul.d-modtab'):
                yield from pagelist(r.css(li)[1], callback=s.parse)

            makerlist = 'div.d-boxpicdata'
            sel['name'] = 'span.d-ttllarge::text'
            sel['desc'] = 'p::text'

        else:
            for td in ('td.makerlist-box-t2', 'td.initial'):
                yield from pagelist(r, selector=td, callback=s.parse)

            makerlist = 'td.w50'
            sel['name'] = 'a::text'
            sel['desc'] = 'div::text'

        for mk in r.css(makerlist):
            maker = { k: mk.css(v).extract_first() for k, v in sel.items() }
            yield Request(r.urljoin(maker['link']), callback=s.ars.parse, meta={'item': maker})
