from xmlrpc.client import ServerProxy

from dmm import url_for


ARIA_SERVER = 'http://localhost:6800/rpc'
TOKEN = 'token:asdfghjkl'


class AriaPipeline(object):

    def open_spider(self, spider):
        self.c = ServerProxy(ARIA_SERVER, allow_none=True)

    def close_spider(self, spider):
        pass

    def add_download(self, **kwargs):
        self.c.aria2.addUri(TOKEN, (url_for('pics', **kwargs),))

    def process_item(self, item, spider):
        pid = item.get('pid')
        if not pid: return item

        realm = 'movie/adult' if item.get('service') == 'mono' else 'video'
        pic = {**item, '_pid': pid, 'realm': realm}
        samples = item.get('samples', 0)

        self.add_download(pic_i='pl', **pic)
        for i in range(samples):
            self.add_download(pic_i='jp-%d' % (i+1), **pic)

        return item
