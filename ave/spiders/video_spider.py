from generics import JAVSpider
from generics import extract_a, extract_t


class VideoSpider(JAVSpider):
    name = 'ave.video'

    def parse(self, response):
        item = {
            'url': response.url,
            'title': extract_t(response.xpath('//h2/text()')),
        }

        yield item

        return

        main = response.xpath('//div[@class="main-subcontent-page"]/div[1]')
        detail = response.xpath('//div[@id="detailbox"]')

        for li in main.xpath('.//li'):
            data = tuple(extract_a(li))
            if data:
                print(data)
            else:
                print(li)
            #print(li.xpath('span/text()|text()'))

        mutual = extract_a(response.xpath('//div[@id="mini-tabs"]'))
        item['mutual'] = tuple(sorted(i[0] for i in mutual))


    def test(self, response):

        #print(detailbox[0].xpath('ol').extract())

        articles = list(get_params('keyword', detailbox[1]))
        for k in (o2m+('actress',)):
            articles.extend(get_params(k, maincontent))

        for a in articles: yield a

        table = {k: v for k, v in self.get_table(maincontent, articles)}

        vid = {
            'cid': response.css('div.top-title::text').re_first('商品番号: (.*)'),
            'title': response.css('h2::text').extract_first(),
            'related': related_ids,
        }

        yield {**item, **vid, **table}
