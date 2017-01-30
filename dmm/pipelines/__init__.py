from scrapy.exceptions import DropItem

from dmm import realms

from .database import DatabasePipeline, MakerPipeline
from .filewriter import FilewriterPipeline


def valid_realm(item):
    return any(all(item[k] == r[k] for k in r) for r in realms.values())


class DmmPipeline(object):

    tally_categories = ('video', 'article', 'mutual')

    def open_spider(self, spider):
        self.count = { c: 0 for c in self.tally_categories }

    def close_spider(self, spider):
        for c in self.tally_categories:
            spider.logger.info("%s processed: %s" % (c.capitalize(), self.count[c]))

    def process_item(self, item, spider):
        if 'article' in item:
            if not item.get('name'):
                spider.logger.warning("No name: {article} {id}".format(**item))
            self.count['article'] += 1
        elif 'mutual' in item:
            item['mutual'] = tuple(i for i in item['mutual'] if valid_realm(i))
            self.count['mutual'] += 1
        else:
            self.count['video'] += 1

        #spider.logger.info(item)
        return item
