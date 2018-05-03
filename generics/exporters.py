from scrapy.exporters import BaseItemExporter
from scrapy.utils.python import to_bytes


class URLItemExporter(BaseItemExporter):

    def __init__(self, file, **kwargs):
        self.file = file

    def export_item(self, item):
        url = item.get('url')
        if not url or not isinstance(url, str):
            return
        self.file.write(to_bytes(url + '\n'))
