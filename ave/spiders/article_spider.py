from . import *


class ArticleSpider(AVESpider):
    name = 'ave.article'

    def __init__(self, article=None, ids=None, **kwargs):
        if article is None or ids is None: return
        super().__init__(**kwargs)
        self.base_url = article

        ids = set(int(i) for i in ids.split(','))
        self.start_urls = tuple({'article': article, 'id': i} for i in ids)

    def parse(self, response):
        item = response.meta.get('params', {})

        if 'name' not in item:
            item['name'] = response.css('h3.block a::text').extract_first()

        ct = response.css('div.column1 strong::text').extract_first()
        if ct:
            item['count'] = int(ct)

        yield item


class ActressSpider(AVESpider):
    name = 'ave.actress'
    base_url = 'actress'

    def __init__(self, names=None, **kwargs):
        if names is None: return
        super().__init__(**kwargs)

        names = set(names.split(','))
        self.start_urls = tuple({'article': 'actress', 'id': n} for n in names)

    def parse(self, response):
        item = response.meta.get('params', {})

        if all(x.isalpha() or x.isspace() for x in item.get('name', '1')):
            item['roma'] = item['name']
            del item['name']

        if 'name' not in item:
            item['name'] = response.css('h3.block a::text').extract_first()

        if 'roma' not in item:
            rl = next(get_params('actress', response.css('span.idol-link a'))).get('id')
            if rl:
                item['roma'] = rl
            
        ct = response.css('div.column1 strong::text').extract_first()
        if ct:
            item['count'] = int(ct)

        del item['id']
        yield item
