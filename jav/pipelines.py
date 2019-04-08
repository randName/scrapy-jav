from os import makedirs
from os.path import exists, dirname

from scrapy.exporters import JsonLinesItemExporter


def merge(fn, new):
    from json import load
    with open(fn) as f:
        old = load(f)

    seqs = (list, tuple, set)

    for k, v in new.items():
        if k in old:
            oldv = old[k]
            if v == oldv:
                continue
            elif type(oldv) in seqs and isinstance(v, set):
                v.update(set(oldv))
        old[k] = v

    return old


class JsonWriterPipeline(object):
    """Pipeline to save scraped items into JSON files."""

    dump_config = {
        'sort_keys': True,
        'ensure_ascii': False,
    }

    def open_spider(self, spider):
        try:
            ow = int(spider.settings.get('JSON_OVERWRITE', 0))
        except ValueError:
            ow = 0
        self.overwrite = ow

        self.json_filename = getattr(spider, 'json_filename', '')

        self.out = spider.settings.get('JSON_DIR')
        if self.out:
            spider.logger.info("Writing files to %s" % self.out)

    def process_item(self, item, spider):
        try:
            jsfn = self.json_filename.format(**item)
        except KeyError:
            return item

        if not jsfn:
            return item

        if self.out is None:
            return item

        fn = '%s/%s' % (self.out, jsfn)

        if exists(fn):
            if not self.overwrite:
                return item
            if self.overwrite == 1:
                item = merge(fn, item)

        for k, v in item.items():
            if isinstance(v, set):
                item[k] = sorted(v)

        makedirs(dirname(fn), exist_ok=True)

        with open(fn, 'wb') as f:
            exporter = JsonLinesItemExporter(f, **self.dump_config)
            exporter.export_item(item)

        item.pop('url', None)
        return item
