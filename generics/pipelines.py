from json import dump
from os import makedirs
from os.path import exists, dirname


def merge(fn, new):
    from json import load
    with open(fn) as f:
        old = load(f)

    seqs = (list, tuple, set)

    for k, v in old.items():
        if k in new:
            newv = new[k]
            if type(v) in seqs and isinstance(newv, set):
                v = set(v)
                v.update(newv)
            else:
                v = newv
        new[k] = v

    return new


class JSONWriterPipeline(object):
    """Pipeline to save scraped items into JSON files."""

    dump_config = {
        'indent': '\t',
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
        except KeyError as e:
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

        with open(fn, 'w') as f:
            dump(item, f, **self.dump_config)

        item.pop('url', None)
        return item
