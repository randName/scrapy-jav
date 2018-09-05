from scrapy import Spider


class JAVSpider(Spider):
    """Custom Spider class for JAV scrapers.

    Allow file containing `start_urls` to be specified on command line.
    """
    start_urls = ()

    custom_settings = {
        'ITEM_PIPELINES': {
            'generics.pipelines.JSONWriterPipeline': 300,
        },
        'DOWNLOADER_MIDDLEWARES': {
            'generics.downloadermiddlewares.XPathRetryMiddleware': 540,
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

    def export_part(self, response):
        return ()

    def export_item(self, response):
        pass

    def export_links(self, response):
        xp = getattr(self, 'export_xpath', None)
        if not xp:
            return ()

        for url in response.xpath(xp).xpath('.//a/@href').extract():
            if self.ignore_url(url):
                continue
            yield response.follow(url, meta={'export': True})

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

        if response.meta.get('export'):
            yield self.export_item(response)
        else:
            yield from self.pagination(response)
            yield from self.export_links(response)

        yield from self.export_part(response)


class ListMixin:
    """Mixin for scraping listings.

    Ensures pages do not get filtered as they may shift.
    """

    def parse(self, response):
        if response.meta.get('export'):
            yield self.export_item(response)
        else:
            yield from self.export_links(response)
            yield from self.pagination(response, dont_filter=True)
