from ..models import db, Video, Mutual, Article


class DatabasePipeline(object):

    def open_spider(self, spider):
        self.itemcount = 0
        db.create_all()

    def close_spider(self, spider):
        db.safe('commit')

    def process_item(self, item, spider):
        if 'mutual' in item:
            m = None
            videos = []
            for i in item['mutual']:
                v = Video.get_or_create(**i)
                if v.mutual:
                    m = v.mutual
                else:
                    videos.append(v)

            if m is None:
                m = Mutual.create()

            for v in videos:
                v.mutual = m

        elif 'article' in item:
            a = Article.get_or_create(**item, update=True)
        else:
            v = Video.get_or_create(**item)

            if not v.mutual:
                v.mutual = Mutual.create()

        self.itemcount += 1
        if self.itemcount % 2000 == 0:
            db.safe('commit')

        return item
