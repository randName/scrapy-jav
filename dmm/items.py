from generics.loader import JAVLoader
from generics.items import Video, Article
from generics.items import URLField, StringField, ArticleField


class DMMVideo(Video):
    cover = URLField()
    description = StringField()
    mutual = URLField(multi=True)
    gallery = URLField(multi=True)
    articles = ArticleField()
    runtime = StringField()
    date = StringField()
    cid = StringField()


class DMMVideoLoader(JAVLoader):
    default_item_class = DMMVideo


class DMMArticle(Article):
    pass
