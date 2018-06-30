from scrapy import Item, Field
from scrapy.loader.processors import MapCompose, Compose, TakeFirst


class URLField(Field):

    def __init__(self, multi=False):
        if not multi:
            self['output_processor'] = TakeFirst()


class StringField(Field):

    def __init__(self):
        self['input_processor'] = MapCompose(str.strip)
        self['output_processor'] = TakeFirst()


class ArticleField(Field):

    def __init__(self):
        self['output_processor'] = Compose(set, sorted)


class Video(Item):
    url = URLField()
    title = StringField()


class Article(Item):
    url = URLField()
    name = StringField()
