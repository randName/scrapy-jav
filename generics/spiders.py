from scrapy import Spider


class JAVSpider(Spider):
    """Custom Spider class for JAV scrapers.

    Allow file containing `start_urls` to be specified on command line.
    Saves all other passed parameters into `custom_settings`.
    """
    start_urls = ()

    custom_settings_base = {
        'ITEM_PIPELINES': {
            'generics.pipelines.JSONWriterPipeline': 300,
        },
        'DOWNLOADER_MIDDLEWARES': {
            'generics.downloadermiddlewares.XPathRetryMiddleware': 540,
        }
    }

    def __init__(self, start=None, **kwargs):
        self.__dict__.update(kwargs)

        if getattr(self, 'custom_settings') is None:
            self.custom_settings = {}

        self.custom_settings.update(self.custom_settings_base)

        if start is not None:
            try:
                with open(start) as f:
                    self.start_urls = tuple(l.strip() for l in f.readlines())
            except OSError:
                self.start_urls = (start,)


class ListSpider(JAVSpider):
    """Class for generic paginated link scraping.

    Ensures pages do not get filtered as they may shift.
    """

    def ignore_url(self, url):
        return False

    def export_item(self, response):
        raise NotImplementedError

    def export_links(self, response):
        xp = getattr(self, 'export_xpath')
        if not xp:
            raise NotImplementedError

        for url in response.xpath(xp).xpath('.//a/@href').extract():
            if self.ignore_url(url):
                continue
            yield url

    def pagination(self, response):
        xp = getattr(self, 'pagination_xpath')
        if not xp:
            raise NotImplementedError

        for a in response.xpath(xp).xpath('.//a'):
            try:
                page = int(a.xpath('text()').extract_first())
            except ValueError:
                continue

            url = a.xpath('@href').extract_first()
            if self.ignore_url(url):
                continue

            yield url, page

    def parse(self, response):
        if response.meta.get('export'):
            yield self.export_item(response)
        else:
            for url, page in self.pagination(response):
                p = {'page': page}
                yield response.follow(url, meta=p, dont_filter=True)

            for url in self.export_links(response):
                yield response.follow(url, meta={'export': True})
