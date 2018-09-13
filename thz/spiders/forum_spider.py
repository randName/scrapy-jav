from generics.spiders import JAVSpider


class ForumSpider(JAVSpider):
    name = 'thz.forum'

    pagination_xpath = '(//div[@class="pg"])[1]'

    start_urls = (
        'http://thz6.com/forum-220-1.html',
    )

    link_xpath = '//td[@class="num"]'

    def export_item(self, response):
        yield from self.links(response, self.link_xpath, export=True)
