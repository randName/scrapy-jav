from . import ArticleSpider

xp = {
    'url': './/a/@href',
    'name': './/a/text()',
    'image': './/img/@src',
}


class StudioSpider(ArticleSpider):
    name = 'ave.studios'

    start_urls = (
        'http://aventertainments.com/studiolists.aspx?Dept_ID=29',
        'http://aventertainments.com/ppv/ppv_studiolists.aspx',
    )

    def export_item(self, response):
        for cell in response.xpath('//td[@class="table-border"]'):
            yield self.get_article(**{
                k: cell.xpath(v).extract_first() for k, v in xp.items()
            })
