from . import *


class MakerSpider(DMMSpider):
    name = 'dmm.maker'
    base_url = DMMSpider.base_url + '{service}/{shop}/-/maker/=/keyword={kw}'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.start_urls = {'kw': 'a'},

    def parse(self, response):
        def get_digital_pages(response):
            for li in ('ul.d-modsort-la', 'ul.d-modtab'):
                for url in DMMSpider.pagelist(response.css(li)[1]):
                    yield Request(response.urljoin(url))

        def get_mono_pages(response):
            for td in ('td.makerlist-box-t2', 'td.initial'):
                for url in DMMSpider.pagelist(response, selector=td):
                    yield Request(response.urljoin(url))

        sel = {
            'url': href,
            'pic': isrc,
        }

        item = response.meta.get('params', {})

        if item.get('service', 'digital') == 'digital':
            get_pages = get_digital_pages
            makerlist = 'div.d-boxpicdata'
            sel['name'] = 'span.d-ttllarge::text'
            sel['desc'] = 'p::text'
        else:
            get_pages = get_mono_pages
            makerlist = 'td.w50'
            sel['name'] = 'a::text'
            sel['desc'] = 'div::text'

        yield from get_pages(response)

        for mk in response.css(makerlist):
            maker = { k: mk.css(v).extract_first() for k, v in sel.items() }
            try:
                a = next(self.get_articles((maker['url'],)))
            except StopIteration:
                continue
            yield ArticleSpider.make_request({**maker, **a})
