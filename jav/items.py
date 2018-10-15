from scrapy import Field, Item
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, Compose, TakeFirst


class Number:

    def __init__(self, t=float):
        self.t = t

    def __call__(self, values, loader_context=None):
        for v in values:
            try:
                yield self.t(v)
            except ValueError:
                yield 0


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


class NumberField(Field):

    def __init__(self, t=float):
        self['input_processor'] = Number(t)
        self['output_processor'] = TakeFirst()


class Video(Item):
    title = StringField()


class JAVLoader(ItemLoader):

    def nested(self, **context):
        return self.__class__(item=self.item, parent=self, **context)
