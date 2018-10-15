from generics.loader import JAVLoader
from generics.items import Video, Article
from generics.items import URLField, StringField, ArticleField


class DMMVideo(Video):
    cid = StringField()
    shop = StringField()
    date = StringField()
    runtime = StringField()
    articles = ArticleField()
    description = StringField()
    delivery_date = StringField()

    cover = URLField()
    gallery = URLField(multi=True)
    related = URLField(multi=True)


class DMMVideoLoader(JAVLoader):
    default_item_class = DMMVideo


class DMMArticle(Article):
    pass
