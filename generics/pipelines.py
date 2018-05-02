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
        self.out = spider.custom_settings.get('JSON_DIR')
        try:
            ow = int(spider.custom_settings.get('JSON_OVERWRITE', 0))
        except ValueError:
            ow = 0
        self.overwrite = ow
        self.dump_config.update(spider.custom_settings.get('JSON_CONFIG', {}))

        if self.out:
            spider.logger.info("Writing files to %s" % self.out)

        try:
            lg = int(spider.custom_settings.get('JSON_LOGITEM', 0))
        except ValueError:
            lg = 0
        self.log = lg

    def process_item(self, item, spider):

        try:
            jsfn = item.pop('JSON_FILENAME')
        except KeyError:
            return

        try:
            jsfn = jsfn.format(**item)
        except KeyError as e:
            spider.logger.warn('KeyError: %s\n%s' % (e, item))
            return

        if self.log:
            msg = 'Writing {item} to {jsfn}'.format(item=item, jsfn=jsfn)
            if self.log == 1:
                spider.logger.debug(msg)
            elif self.log == 2:
                spider.logger.info(msg)

        if self.out is None:
            return

        fn = '%s/%s' % (self.out, jsfn)

        if exists(fn):
            if not self.overwrite:
                return
            if self.overwrite == 1:
                item = merge(fn, item)

        for k, v in item.items():
            if isinstance(v, set):
                item[k] = sorted(v)

        makedirs(dirname(fn), exist_ok=True)

        with open(fn, 'w') as f:
            dump(item, f, **self.dump_config)
