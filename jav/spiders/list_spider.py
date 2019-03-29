from . import JAVSpider


class UrlListSpider(JAVSpider):

    deep = False

    def get_list(self, response):
        yield

    def parse_item(self, response):
        if response.meta.get('deep'):
            response.meta['export'] = self.export_items(response)
            return ()

        urls = self.get_list(response)

        if self.deep:
            for url in urls:
                yield response.follow(url, meta={'deep': True})
        else:
            for url in urls:
                yield {'url': url}
