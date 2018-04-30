from generics.spiders import JAVSpider

JSON_FILENAME = '{type}/articles/{article}/{id}.json'


class ArticleSpider(JAVSpider):
    name = 'ave.article'

    def parse(self, response):
        keys = ('article', 'id', 'name', 'type')
        try:
            item = {k: response.meta[k] for k in keys}
        except KeyError:
            return

        item['JSON_FILENAME'] = JSON_FILENAME.format(**item)

        yield item
