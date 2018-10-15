from jav.utils import extract_a
from . import ArticleSpider


class SubdeptSpider(ArticleSpider):
    name = 'ave.subdept'

    start_urls = (
        'https://www.aventertainments.com/categorylists.aspx?Dept_ID=29',
        'https://www.aventertainments.com/ppv/ppv_categorylists.aspx',
    )

    def export_item(self, response):
        for section in response.xpath('//div[@class="row2"]'):
            sname = section.xpath('h1/text()').extract_first()

            for url, t in extract_a(section):
                if url.startswith('#'):
                    continue
                yield self.get_article(url, name=t, category=sname)
