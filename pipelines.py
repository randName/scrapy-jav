from os.path import join
from xmlrpc.client import ServerProxy


class AriaPipeline(object):

    def open_spider(self, spider):
        self.dir = spider.settings.get('ARIA_DIR', '~/')
        self.rpc = spider.settings.get('ARIA_RPC', '')
        self.c = ServerProxy(self.rpc, allow_none=True)
        self.token = spider.settings.get('ARIA_TOKEN')

    def process_item(self, item, spider):
        folder = item.get('pid', '')
        images = item.get('image_urls', ())
        spider.logger.debug("Aria: %d images" % len(images))
        for image in images:
            self.c.aria2.addUri(self.token, (image,), {'dir': join(self.dir, folder)})
        return item
