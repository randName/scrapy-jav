from generics.spiders import JAVSpider
from generics.utils import extract_a, extract_t, parse_url, get_key

JSON_FILENAME = 'videos/{studio}/{pid}.json'


class VideoSpider(JAVSpider):
    name = 'ave.video'

    def parse(self, response):

        pid = get_key(response.url, 'product_id')

        if not pid:
            print(response.url)
            return

        studio = ''

        item = {
            'pid': pid,
            'studio': studio,
            'url': response.url,
            'title': extract_t(response.xpath('//h2')),
        }

        item['JSON_FILENAME'] = JSON_FILENAME.format(**item)
