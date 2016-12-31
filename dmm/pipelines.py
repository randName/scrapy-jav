# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from os import fsync, makedirs
from xmlrpc.client import ServerProxy

TOKEN = 'token:asdfghjkl'
PIC_PATH = 'http://pics.dmm.co.jp/{0}/{1}/{1}'

DATA_PATH = 'data'
FOLDERS = ('joins', 'videos', 'articles', 'misc')
KEYS = ('date','cid','pkg','runtime','maker','label','series','director')
MISC = ('cid','title','description')


class DmmPipeline(object):

    def open_spider(self, spider):
        self.c = ServerProxy('http://localhost:6800/rpc', allow_none=True)
        self.videocount = 0
        for c in FOLDERS:
            setattr(self, c, {})
            makedirs('%s/%s' % (DATA_PATH, c), exist_ok=True)

    def close_spider(self, spider):
        for c in FOLDERS:
            for f in getattr(self, c).values():
                f.close()

    def filewrite(self, s, t, k):
        try:
            f = getattr(self, t)[k]
        except KeyError:
            f = open('%s/%s/%s.csv' % (DATA_PATH, t, k), 'w')
            getattr(self, t)[k] = f
        print(s, file=f)

    def adl(self, url):
        self.c.aria2.addUri(TOKEN, (url,))

    def get_images(self, realm, pkg, samples):
        p = PIC_PATH.format(realm, pkg)
        self.adl(p+'pl.jpg')
        for i in range(samples):
            self.adl('%sjp-%d.jpg' % (p, i+1))

    def process_item(self, item, spider):
        if 'article' in item:
            s = '{id},{name}'.format(**item)
            self.filewrite(s, 'articles', item['article'])
        elif 'related' in item:
            s = ','.join('{shop}/{cid}'.format(**i) for i in item['related'])
            self.filewrite(s, 'misc', 'related')
        else:
            self.get_images('digital/video', item['pkg'], item['samples'])

            if item['date']:
                dt = item['date'].split('/')
                if int(dt[0]) < 2000:
                    fn = 'pre_2000'
                else:
                    fn = '_'.join(dt[:2])
            else:
                fn = 'no_date'

            for d, n, c in (('videos', fn, KEYS), ('misc', 'unicode', MISC)):
                self.filewrite(','.join(str(item.get(k, '')) for k in c), d, n)

            for k in ('keyword', 'actress', 'histrion'):
                if k not in item: continue
                self.filewrite(
                    '\n'.join('%s,%s' % (i, item['cid']) for i in item[k]),
                    'joins', k
                )

            self.videocount += 1
            if ( self.videocount % 1000 == 0 ):
                print('Scraped %d videos' % self.videocount)
                for c in FOLDERS:
                    for f in getattr(self, c).values():
                        f.flush()
                        fsync(f.fileno())
