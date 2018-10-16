from jav.utils import extract_a
from jav.spiders import JAVSpider

from ..article import get_article, parse_article


class ArticleSpider(JAVSpider):
    name = 'ave.article'

    def export_items(self, response):
        yield parse_article(response)


class StudioSpider(JAVSpider):
    name = 'ave.studios'

    start_urls = (
        'http://aventertainments.com/studiolists.aspx?Dept_ID=29',
        'http://aventertainments.com/ppv/ppv_studiolists.aspx',
    )

    def export_items(self, response):
        for cell in response.xpath('//td[@class="table-border"]'):
            url, t = next(extract_a(cell))

            m = get_article(url, name=t)
            if m is None:
                continue

            m['url'] = response.urljoin(url)

            img = cell.xpath('.//img/@src').extract_first()
            if img:
                m['image'] = img

            yield m


class SubdeptSpider(JAVSpider):
    name = 'ave.subdept'

    start_urls = (
        'https://www.aventertainments.com/categorylists.aspx?Dept_ID=29',
        'https://www.aventertainments.com/ppv/ppv_categorylists.aspx',
    )

    def export_items(self, response):
        for section in response.xpath('//div[@class="row2"]'):
            sname = section.xpath('h1/text()').extract_first()

            for url, t in extract_a(section):
                if url.startswith('#'):
                    continue

                item = get_article(url, name=t, category=sname)
                if item:
                    item['url'] = response.urljoin(url)
                    yield item
