from scrapy.loader import ItemLoader


class JAVLoader(ItemLoader):

    def nested(self, **context):
        return self.__class__(item=self.item, parent=self, **context)
