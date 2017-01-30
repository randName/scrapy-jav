from dmm import realms, o2m, m2m, db_url
from database import Database, Base, Table, Column, ForeignKeyConstraint
from database import ForeignKey, Integer, String, Date, Text, Enum
from database import relationship, association_proxy, declared_attr

db = Database(db_url)

service_enum = Enum(*(r['service'] for r in realms.values()), name='service')

video_m2m = {k: Table(
    '%s_videos' % k, Base.metadata,
    Column('%s_id' % k, ForeignKey('%s.id' % k), primary_key=True),
    Column('video_service', service_enum, primary_key=True),
    Column('video_cid', String(20), primary_key=True),
    ForeignKeyConstraint(
        ('video_cid', 'video_service'), ('video.cid', 'video.service')
    )
) for k in m2m}


class Video(Base):
    __tablename__ = 'video'

    service = Column(service_enum, primary_key=True)
    cid = Column(String(20), primary_key=True)
    title = Column(Text)
    description = Column(Text)

    mutual_id = Column(Integer, ForeignKey('mutual.id'))
    mutual = relationship('Mutual', back_populates='videos')

    date = Column(Date)
    runtime = Column(Integer)

    pid = Column(String(20))
    samples = Column(Integer)

    maker_id = Column(Integer, ForeignKey('maker.id'))
    label_id = Column(Integer, ForeignKey('label.id'))
    series_id = Column(Integer, ForeignKey('series.id'))
    director_id = Column(Integer, ForeignKey('director.id'))
    keyword_ids = association_proxy(
        'keywords', 'id', creator=lambda i: Keyword.get_or_create(i)
    )
    actress_ids = association_proxy(
        'actresses', 'id', creator=lambda i: Actress.get_or_create(i)
    )
    histrion_ids = association_proxy(
        'histrions', 'id', creator=lambda i: Histrion.get_or_create(i)
    )
    
    maker = relationship('Maker')
    label = relationship('Label')
    series = relationship('Series')
    director = relationship('Director')
    keywords = relationship('Keyword', secondary='keyword_videos')
    actresses = relationship('Actress', secondary='actress_videos')
    histrions = relationship('Histrion', secondary='histrion_videos')

    def __init__(self, service, cid, **kwargs):
        self.service = service
        self.cid = cid
        self.update(**kwargs)

    def update(self, **kwargs):
        for k, v in kwargs.items():
            if k in o2m:
                setattr(self, k, Article.get_or_create(article=k, id=v))
            elif k in m2m:
                prop = getattr(self, k+'_ids')
                prop.extend(v.difference(prop))
            else:
                setattr(self, k, v)

    @property
    def details(self):
        return '{v.cid}\t{v.title}'.format(v=self)

    def __str__(self):
        return self.cid

    def __repr__(self):
        return '<Video %s>' % self.cid

    @classmethod
    def get_or_create(cls, service, cid, update=True, **kwargs):
        v = db.session.query(cls).filter_by(service=service, cid=cid).first()
        if not v:
            v = cls(service, cid, **kwargs)
            db.session.add(v)
        elif update:
            v.update(**kwargs)
        return v

    @classmethod
    def get(cls, cid):
        return db.session.query(cls).filter_by(cid=cid).order_by('service').first()

    @classmethod
    def filter_by(cls, **kwargs):
        return db.session.query(cls).filter_by(**kwargs)


class Mutual(Base):
    __tablename__ = 'mutual'

    id = Column(Integer, primary_key=True)
    videos = relationship(
        'Video', back_populates='mutual', order_by=lambda: Video.service
    )

    def __str__(self):
        return '%s: %s' % (self.id, self.videos)

    def __repr__(self):
        return '<Mutual %s>' % self.id

    @classmethod
    def create(cls):
        m = cls()
        db.session.add(m)
        return m


class Article(object):
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id = Column(Integer, primary_key=True, autoincrement=False)
    name = Column(String(40))

    def __init__(self, id, **kwargs):
        self.id = id
        self.update(**kwargs)

    def update(self, **kwargs):
        for k, v in kwargs.items():
            if v and hasattr(self, k):
                setattr(self, k, v)

    def __str__(self):
        return self.name if self.name else ''

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, self.id)

    @classmethod
    def get_or_create(cls, id, article=None, update=False, **kwargs):
        try:
            article = globals()[article.capitalize()]
        except (KeyError, AttributeError):
            article = cls

        a = db.session.query(article).get(id)
        if not a:
            a = article(id, **kwargs)
            db.session.add(a)
        elif update:
            a.update(**kwargs)
        return a


class Maker(Article, Base):
    pass


class Label(Article, Base):
    pass


class Director(Article, Base):
    pass


class Actress(Article, Base):
    pass


class Histrion(Article, Base):
    pass


class Keyword(Article, Base):
    pass


class Series(Article, Base):
    name = Column(Text)
