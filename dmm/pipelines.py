# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


class DmmPipeline(object):

    def open_spider(self, spider):
        self.articles = {}
        self.videos = {}
        self.misc = open('misc.csv', 'w')
        self.keyword = open('keywords.csv', 'w')
        self.actress = open('actresses.csv', 'w')

    def close_spider(self, spider):
        for f in self.articles.values():
            f.close()
        for f in self.videos.values():
            f.close()
        self.misc.close()
        self.keyword.close()
        self.actress.close()

    def process_item(self, item, spider):
        if 'article' in item:
            return item
            article = item['article']
            f = self.get_file('articles', article)
            print('{id},{name}'.format(**item), file=f)
        else:
            if '/' in item['date']:
                d = item['date'].split('/')
            else:
                d = ('no', 'date', 0)
            ks = ('cid', 'runtime', 'maker', 'label', 'series', 'director')
            s = d[2] + ',' + ','.join(self.get_keys(item, ks))
            print(s, file=self.get_file('videos', '_'.join(d[:2])))
            ks = ('cid', 'pkg', 'samples', 'title')
            s = ','.join(self.get_keys(item, ks))
            print(s, file=self.misc)
            for k in ('keyword', 'actress'): self.m2m(k, item)

    def get_keys(self, item, keys):
        for k in keys:
            try:
                yield str(item[k])
            except KeyError:
                yield ''

    def m2m(self, k, item):
        try:
            s = '\n'.join('%s,%s' % (item['cid'], i) for i in item[k])
            print(s, file=getattr(self, k))
        except KeyError:
            pass

    def get_file(self, t, k):
        try:
            return getattr(self, t)[k]
        except KeyError:
            f = open('%s/%s.csv' % (t, k), 'w')
            getattr(self, t)[k] = f
        return f
