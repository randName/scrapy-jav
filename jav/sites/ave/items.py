from jav.loader import JAVLoader
from jav.items import Video
from jav.items import URLField, StringField, ArticleField, NumberField


class AVEVideo(Video):
    pid = NumberField(int)
    vid = StringField()
    shop = StringField()
    date = StringField()
    runtime = StringField()
    articles = ArticleField()
    description = StringField()

    cover = URLField()
    gallery = URLField(multi=True)
    related = URLField(multi=True)


class AVEVideoLoader(JAVLoader):
    default_item_class = AVEVideo
