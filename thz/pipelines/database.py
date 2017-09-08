from ..models import db, Thread


class DatabasePipeline(object):

    def open_spider(self, spider):
        db.create_all()

    def close_spider(self, spider):
        db.safe('commit')

    def process_item(self, item, spider):
        #print("%r\t%r\t%r" % (item['cid'], item['date'], item['title']))

        t = Thread.get(item.get('id'))
        if not t:
            t = Thread(**item)
            db.session.add(t)

        return item
