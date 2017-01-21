from . import *


def get_digital_pages(response):
    for li in ('ul.d-modsort-la', 'ul.d-modtab'):
        for url in pagelist(response.css(li)):
            yield url

def get_mono_pages(response):
    for td in ('td.makerlist-box-t2', 'td.initial'):
        for url in pagelist(response, selector=td):
            yield url


class MakerSpider(DMMSpider):
    name = 'dmm.maker'
    base_url = 'maker'

    custom_settings = {
        'ITEM_PIPELINES': {
            'dmm.pipelines.DmmPipeline': 300,
        },
    }

    def __init__(self, deep=False, **kwargs):
        super().__init__(**kwargs)
        self.deep = deep
        self.start_urls = {'keyword': 'a'},

    def parse(self, response):
        item = response.meta.get('params', {})

        if item.get('service') == 'mono':
            get_pages = get_mono_pages
            makerlist = 'td.w50'
        else:
            get_pages = get_digital_pages
            makerlist = 'div.d-boxpicdata'

        for url in get_pages(response):
            yield Request(response.urljoin(url), meta={'params': item})

        for mk in response.css(makerlist):
            maker = parse_url('article', mk.xpath('a/@href').extract_first())
            if not maker: continue
            maker['pic'] = mk.css('img::attr(src)').extract_first()
            maker['id'] = int(maker['id'])

            txt = mk.xpath('.//text()').extract()
            p = tuple(t.strip('\n') for t in txt if t != '\n')
            maker['name'] = p[0]

            if len(p) == 2:
                maker['description'] = p[1]

            if self.deep:
                yield ArticleSpider.make_request(maker)
            else:
                yield maker
