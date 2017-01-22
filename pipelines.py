from xmlrpc.client import ServerProxy


class AriaPipeline(object):

    def open_spider(self, spider):
        self.rpc = spider.settings.get('ARIA_RPC', '')
        self.c = ServerProxy(self.rpc, allow_none=True)
        self.token = spider.settings.get('ARIA_TOKEN')

    def process_item(self, item, spider):
        images = item.get('image_urls')
        if images:
            spider.logger.debug("Aria: %d images" % len(images))
            self.c.aria2.addUri(self.token, images)
        return item
