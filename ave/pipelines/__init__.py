from scrapy.exceptions import DropItem


class AvePipeline(object):

    tally_categories = ('video', 'article')

    def open_spider(self, spider):
        self.count = { c: 0 for c in self.tally_categories }

    def close_spider(self, spider):
        for c in self.tally_categories:
            spider.logger.info("%s processed: %s" % (c.capitalize(), self.count[c]))

    def process_item(self, item, spider):
        if item.get('article') == 'video':
            self.count['video'] += 1
        else:
            if not item.get('name'):
                spider.logger.warning("No name: {article} {id}".format(**item))
            self.count['article'] += 1

        spider.logger.info(item)
        return item
