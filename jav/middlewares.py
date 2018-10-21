from scrapy.exceptions import IgnoreRequest
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.spidermiddlewares.httperror import HttpErrorMiddleware


class XPathRetryMiddleware(RetryMiddleware):
    """Middleware to retry a request if a specified xpath is not present"""

    max_retry_times = 2
    priority_adjust = 0

    def __init__(self, settings):
        pass

    def process_response(self, request, response, spider):
        xp = getattr(spider, 'retry_xpath', None)
        if xp is None:
            return response

        if response.url.endswith('robots.txt'):
            return response

        if response.status == 200 and not response.xpath(xp):
            reason = 'could not find xpath "{}"'.format(xp)
            return self._retry(request, reason, spider) or response

        return response


class NotFound(IgnoreRequest):
    pass


class NotFoundMiddleware(HttpErrorMiddleware):

    def __init__(self, settings):
        pass

    def process_spider_input(self, response, spider):
        if response.status == 404:
            raise NotFound('Page not found')

    def process_spider_exception(self, response, exception, spider):
        if isinstance(exception, NotFound):
            return ()
