from generics.loader import JAVLoader
from generics.items import Video, Article
from generics.items import URLField, StringField, ArticleField


class DMMVideo(Video):
    cover = URLField()
    description = StringField()
    gallery = URLField(multi=True)
    related = URLField(multi=True)
    articles = ArticleField()
    runtime = StringField()
    date = StringField()
    delivery_date = StringField()
    title = StringField()
    shop = StringField()
    cid = StringField()


class DMMVideoLoader(JAVLoader):
    default_item_class = DMMVideo


class DMMArticle(Article):
    pass
