from scrapy.exporters import BaseItemExporter
from scrapy.utils.python import to_bytes


class UrlExporter(BaseItemExporter):

    def __init__(self, file, **kwargs):
        self._configure(kwargs, dont_fail=True)
        self.file = file

    def export_item(self, item):
        url = item.get('url')
        if not url or not isinstance(url, str):
            return
        self.file.write(to_bytes(url + '\n'))
