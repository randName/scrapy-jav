# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from os import fsync
from xmlrpc.client import ServerProxy

TOKEN = 'token:asdfghjkl'
PKG_URL = 'http://pics.dmm.co.jp/digital/video/{0}/{0}pl.jpg'
SMP_URL = 'http://pics.dmm.co.jp/digital/video/{0}/{0}jp-{1}.jpg'
KEYS = ('day', 'cid', 'pkg', 'runtime', 'maker', 'label', 'series', 'director')

class DmmPipeline(object):

    def open_spider(self, spider):
        self.misc = open('data/titles.csv', 'w')
        self.related = open('data/related.csv', 'w')
        for c in ('joins', 'videos', 'articles'):
            setattr(self, c, {})
        self.videocount = 0
        self.c = ServerProxy('http://localhost:6800/rpc', allow_none=True)

    def close_spider(self, spider):
        self.misc.close()
        self.related.close()
        for c in ('joins', 'videos', 'articles'):
            for f in getattr(self, c).values():
                f.close()

    def adl(self, url):
        self.c.aria2.addUri(TOKEN, (url,))

    def get_file(self, t, k):
        try:
            return getattr(self, t)[k]
        except KeyError:
            f = open('data/%s/%s.csv' % (t, k), 'w')
            getattr(self, t)[k] = f
        return f

    def process_item(self, item, spider):
        if 'article' in item:
            article = item['article']
            f = self.get_file('articles', article)
            print('{id},{name}'.format(**item), file=f)
        elif 'related' in item:
            print(','.join(item['related']), file=self.related)
        else:
            self.adl(PKG_URL.format(item['pkg']))
            for i in range(item['samples']):
                self.adl(SMP_URL.format(item['pkg'], i+1))

            if item['date']:
                fn = '_'.join(item['date'][:2])
                item['day'] = item['date'][2]
            else:
                fn = 'no_date'

            print(
                ','.join(str(item.get(k, '')) for k in KEYS),
                file=self.get_file('videos', fn)
            )

            print(
                ','.join(str(item.get(k, '')) for k in ('cid', 'title', 'description')),
                file=self.misc
            )

            for k in ('keyword', 'actress', 'histrion'):
                if k not in item: continue
                print(
                    '\n'.join('%s,%s' % (i, item['cid']) for i in item[k]),
                    file=self.get_file('joins', k)
                )

            self.videocount += 1

            if ( self.videocount % 1000 == 0 ):
                print('Scraped %d videos, writing data to disk' % self.videocount)
                for c in ('joins', 'videos', 'articles'):
                    for f in getattr(self, c).values():
                        f.flush()
                        fsync(f.fileno())
                self.related.flush()
                fsync(self.related.fileno())
                self.misc.flush()
                fsync(self.misc.fileno())
