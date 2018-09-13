from generics.loader import JAVLoader
from generics.items import Video
from generics.items import URLField, StringField, NumberField


class THZVideo(Video):
    tid = NumberField(int)
    cid = StringField()

    fmt = StringField()
    size = StringField()
    torrent = URLField()

    cover = URLField()
    gallery = URLField(multi=True)


class THZVideoLoader(JAVLoader):
    default_item_class = THZVideo
