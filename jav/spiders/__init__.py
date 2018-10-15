from scrapy import Spider, Request


class JAVSpider(Spider):
    """Custom Spider class for JAV scrapers.

    Allow file containing `start_urls` to be specified in settings
    """

    handle_httpstatus_list = (404,)

    start_urls = ()

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

    def make_request(self, url, **kw):
        return Request(url, **kw)

    def start_requests(self):
        for url in self.get_start_urls():
            yield Request(url, dont_filter=True)

        yield from super().start_requests()

    def parse_item(self, response):
        return ()

    def export_items(self, response):
        return ()

    def links(self, response, xp, follow=False, ignore=None, **kw):
        for url in response.xpath(xp).xpath('.//a/@href').extract():
            if ignore and ignore(url):
                continue

            if follow:
                yield response.follow(url, **kw)
            else:
                yield response.urljoin(url)

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
        yield from self.parse_item(response)

        for item in self.export_items(response):
            url = item.pop('url', response.url)
            yield {
                'url': url,
                'item': item,
            }

        yield from self.pagination(response)
