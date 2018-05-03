from scrapy.downloadermiddlewares.retry import RetryMiddleware


class XPathRetryMiddleware(RetryMiddleware):

    def process_response(self, request, response, spider):
        xp = getattr(spider, 'retry_xpath', None)
        if xp is None:
            return response

        if response.status == 200 and not response.xpath(xp):
            reason = 'could not find xpath "{}"'.format(xp)
            return self._retry(request, reason, spider) or response

        return response
