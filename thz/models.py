from thz import db_url
from database import Database, Base, Table, Column, relationship
from database import ForeignKey, Integer, String, Date, Text

db = Database(db_url)


class Thread(Base):
    __tablename__ = 'thread'

    id = Column(Integer, primary_key=True, autoincrement=False)
    cid = Column(String(20))
    date = Column(Date)
    title = Column(Text)
    status = Column(Integer)

    images = relationship('Image', back_populates='thread')
    torrent = relationship('Torrent', back_populates='thread')

    def __init__(self, id, **kwargs):
        self.id = id
        self.update(**kwargs)

    def update(self, **kwargs):
        for k, v in kwargs.items():
            if k == 'images':
                for i in v: Image.create(*i, self.id)
            elif k == 'torrent':
                Torrent.create(**v, tid=self.id)
            else:
                setattr(self, k, v)

    def __str__(self):
        return self.cid

    def __repr__(self):
        return '<Thread %s>' % self.id

    @classmethod
    def get_or_create(cls, id, update=True, **kwargs):
        t = db.session.query(cls).filter_by(id=id).first()
        if not t:
            t = cls(id, **kwargs)
            db.session.add(t)
        elif update:
            t.update(**kwargs)
        return t

    @classmethod
    def get(cls, id):
        return db.session.query(cls).filter_by(id=id).first()

    @classmethod
    def filter_by(cls, **kwargs):
        return db.session.query(cls).filter_by(**kwargs)


class Image(Base):
    __tablename__ = 'image'

    id = Column(Integer, primary_key=True)
    aid = Column(String(20))
    url = Column(Text)

    thread_id = Column(Integer, ForeignKey('thread.id'))
    thread = relationship('Thread', back_populates='images')

    def __init__(self, aid, url, tid):
        self.aid = aid
        self.url = url
        self.thread_id = tid

    def __str__(self):
        return '%s' % self.url

    def __repr__(self):
        return '<Image %s>' % self.aid

    @classmethod
    def create(cls, *args):
        i = cls(*args)
        db.session.add(i)


class Torrent(Base):
    __tablename__ = 'torrent'

    id = Column(Integer, primary_key=True)
    aid = Column(Text)
    name = Column(Text)
    size = Column(Integer)
    status = Column(Integer)
    category = Column(String(5))

    thread_id = Column(Integer, ForeignKey('thread.id'))
    thread = relationship('Thread', back_populates='torrent')

    def __init__(self, aid, name, size, tid):
        self.aid = aid
        self.name = name 
        self.size = size
        self.thread_id = tid

    def __str__(self):
        return '%s' % self.name

    def __repr__(self):
        return '<Torrent %s>' % self.aid

    @classmethod
    def create(cls, **kwargs):
        t = cls(**kwargs)
        db.session.add(t)
