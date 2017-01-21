from os import fsync, makedirs

from dmm import o2m, m2m


DATA_PATH = 'data'
FOLDERS = ('joins', 'videos', 'articles', 'misc')
KEYS = ('date', 'cid', 'pid', 'runtime') + o2m
MISC = ('cid', 'title', 'description')


class FilewriterPipeline(object):

    def open_spider(self, spider):
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

    def process_item(self, item, spider):
        if 'article' in item:
            s = '{id},{name}'.format(**item)
            self.filewrite(s, 'articles', item['article'])
        elif 'mutual' in item:
            s = ','.join('{shop}/{cid}'.format(**i) for i in item['mutual'])
            self.filewrite(s, 'misc', 'mutual')
        else:
            dt = item.get('date')
            if dt:
                fn = 'pre_2000' if dt.year < 2000 else '{:%Y_%m}'.format(dt)
            else:
                fn = 'no_date'

            for d, n, c in (('videos', fn, KEYS), ('misc', 'unicode', MISC)):
                self.filewrite(','.join(str(item.get(k, '')) for k in c), d, n)

            for k in m2m:
                if k not in item: continue
                self.filewrite(
                    '\n'.join('%s,%s' % (i, item['cid']) for i in item[k]),
                    'joins', k
                )

            self.videocount += 1
            if ( self.videocount % 1000 == 0 ):
                spider.logger.debug('Flushing files')
                for c in FOLDERS:
                    for f in getattr(self, c).values():
                        f.flush()
                        fsync(f.fileno())
