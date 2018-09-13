from generics.spiders import JAVSpider
from thz.items import THZVideoLoader

t_re = '.*aid=(.+)&.*'

info = {
    '品番': 'cid',
    '格式': 'fmt',
    '容量': 'size',
    '片名': 'title',
}


class ThreadSpider(JAVSpider):
    name = 'thz.thread'

    json_filename = 'threads/{tid}.json'

    def parse(self, response):
        try:
            tid = response.url.split('-')[1]
        except (IndexError, ValueError):
            return

        v = THZVideoLoader(response=response)
        v.add_value('tid', tid)

        cell = response.xpath('//td[@class="t_f"]')

        for line in cell.xpath('text()').extract():
            try:
                label, text = line.strip().split('：')
                label = info[label]
            except (KeyError, ValueError, IndexError):
                continue

            v.add_value(label, text)

        c = v.nested(selector=cell)
        c.add_xpath('cover', '//img[@inpost="1"]/@file')
        c.add_xpath('torrent', '//div[@class="xs0"]/p/a/@href', re=t_re)
        c.add_xpath('gallery', '//img[@lazyloadthumb="1"]/@file')

        item = v.load_item()
        yield item
