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
                for url in DMMSpider.pagelist(response.css(li)):
                    yield Request(response.urljoin(url))

        def get_mono_pages(response):
            for td in ('td.makerlist-box-t2', 'td.initial'):
                for url in DMMSpider.pagelist(response, selector=td):
                    yield Request(response.urljoin(url))

        item = response.meta.get('params', {})

        if item.get('service', 'digital') == 'digital':
            get_pages = get_digital_pages
            makerlist = 'div.d-boxpicdata'
            sel = {
                'name': 'span.d-ttllarge',
                'description': 'p'
            }
        else:
            get_pages = get_mono_pages
            makerlist = 'td.w50'
            sel = {
                'name': 'a',
                'description': 'div'
            }

        yield from get_pages(response)

        for mk in response.css(makerlist):
            maker = next(self.get_params('article', mk.css(href).extract()))
            maker['pic'] = mk.css(isrc).extract_first()
            for k, v in sel.items():
                maker[k] = mk.css(v+'::text').extract_first()
            yield ArticleSpider.make_request(maker)
