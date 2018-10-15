from scrapy import Spider


class JAVSpider(Spider):
    """Custom Spider class for JAV scrapers.

    Allow file containing `start_urls` to be specified on command line.
    """
    start_urls = ()

    custom_settings = {
        'ITEM_PIPELINES': {
            'jav.pipelines.JsonWriterPipeline': 300,
        },
        'DOWNLOADER_MIDDLEWARES': {
            'jav.downloadermiddlewares.XPathRetryMiddleware': 540,
        }
    }

    def __init__(self, start=None, **kwargs):
        self.__dict__.update(kwargs)

        if start is not None:
            try:
                with open(start) as f:
                    self.start_urls = tuple(l.strip() for l in f.readlines())
            except OSError:
                self.start_urls = (start,)

    def ignore_url(self, url):
        return False

    def export_item(self, response):
        return ()

    def links(self, response, xp, export=False, **kw):
        for url in response.xpath(xp).xpath('.//a/@href').extract():
            if self.ignore_url(url):
                continue

            if export:
                yield {'url': response.urljoin(url)}
            else:
                yield response.follow(url, **kw)

    def pagination(self, response, **kw):
        xp = getattr(self, 'pagination_xpath', None)
        if not xp:
            return ()

        for a in response.xpath(xp).xpath('.//a'):
            try:
                page = int(a.xpath('text()').extract_first())
            except ValueError:
                continue

            url = a.xpath('@href').extract_first()
            if self.ignore_url(url):
                continue

            yield response.follow(url, meta={'page': page}, **kw)

    def parse(self, response):
        if response.status == 404:
            return

        yield from self.export_item(response)
        yield from self.pagination(response)
