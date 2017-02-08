from . import *


class StudioSpider(AVESpider):
    name = 'ave.studios'
    base_url = 'studios'

    def __init__(self, deep=False, **kwargs):
        super().__init__(**kwargs)
        self.deep = deep
        self.start_urls = {},

    def parse(self, response):
        for studio in get_params('studio', response.css('li.studio')):
            if self.deep:
                yield ArticleSpider.make_request(studio)
            else:
                yield studio
