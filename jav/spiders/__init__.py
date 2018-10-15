from scrapy import Spider, Request


class JAVSpider(Spider):
    """Custom Spider class for JAV scrapers.

    Allow file containing `start_urls` to be specified in settings
    """

    handle_httpstatus_list = (404,)

    def get_start_urls(self):
        for url in self.settings.getlist('START_URLS', ()):
            try:
                with open(url) as f:
                    for line in f.readlines():
                        line = line.strip()
                        if line and not line.startswith('#'):
                            yield line
            except OSError:
                yield url

    def start_requests(self):
        for url in self.get_start_urls():
            yield Request(url, dont_filter=True)

        yield from super().start_requests()

    def parse_item(self, response):
        return ()

    def links(self, response, xp):
        yield from response.xpath(xp).xpath('.//a/@href').extract()

    def pagination(self, response, ignore=None, **kw):
        xp = getattr(self, 'pagination_xpath', None)
        if not xp:
            return ()

        max_page = self.settings.getint('MAX_PAGE', 1)

        for a in response.xpath(xp).xpath('.//a'):
            try:
                page = int(a.xpath('text()').extract_first())
            except ValueError:
                continue

            if max_page > 0 and page > max_page:
                continue

            url = a.xpath('@href').extract_first()
            if ignore and ignore(url):
                continue

            yield response.follow(url, meta={'page': page}, **kw)

    def parse(self, response):
        if response.status == 404:
            return

        yield from self.parse_item(response)
        yield from self.pagination(response)
