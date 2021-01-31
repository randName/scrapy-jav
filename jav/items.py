from collections import defaultdict

from scrapy import Field, Item
from scrapy.loader import ItemLoader
from itemloaders.processors import MapCompose, Compose, TakeFirst


def filter_empty(urls):
    for url in urls:
        if not url or url.startswith('#'):
            continue
        yield url


class Unique(Compose):

    def __init__(self, **kw):
        super().__init__(**kw)
        self.functions = (set, sorted)


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
        self['input_processor'] = filter_empty
        self['output_processor'] = Unique() if multi else TakeFirst()


class StringField(Field):

    def __init__(self):
        self['input_processor'] = MapCompose(str.strip)
        self['output_processor'] = TakeFirst()


class ArticleField(Field):

    def __init__(self, parse=None):
        if parse:
            self['input_processor'] = parse
        self['output_processor'] = Unique()


class NumberField(Field):

    def __init__(self, t=float):
        self['input_processor'] = Number(t)
        self['output_processor'] = TakeFirst()


class Video(Item):
    fields = defaultdict(StringField)
    fields.update({
        'image': URLField(),
        'title': StringField(),
        'gallery': URLField(multi=True),
        'related': URLField(multi=True),
        'articles': URLField(multi=True),
    })


class JAVLoader(ItemLoader):

    default_item_class = Video

    def __init__(self, xpaths=None, **kw):
        super().__init__(**kw)

        if xpaths is not None:
            for k, xp in xpaths.items():
                if isinstance(xp, (tuple, list)):
                    for v in xp:
                        self.add_xpath(k, v)
                else:
                    self.add_xpath(k, xp)

    def nested(self, **context):
        return self.__class__(item=self.item, parent=self, **context)
