from json import dump
from os import makedirs
from os.path import exists, dirname

from scrapy.exceptions import DropItem


class JSONWriterPipeline(object):
    """Pipeline to save scraped items into JSON files."""

    dump_config = {
        'indent': '\t',
        'sort_keys': True,
        'ensure_ascii': False,
    }

    def open_spider(self, spider):
        self.out = spider.custom_settings.get('JSON_DIR')
        self.overwrite = spider.custom_settings.get('JSON_OVERWRITE', False)
        self.dump_config.update(spider.custom_settings.get('JSON_CONFIG', {}))

        if self.out:
            spider.logger.info("Writing files to %s" % self.out)

    def process_item(self, item, spider):
        if self.out is None:
            return

        try:
            fn = '%s/%s' % (self.out, item.pop('JSON_FILENAME'))
        except KeyError:
            return

        if exists(fn) and not self.overwrite:
            # raise DropItem("Already scraped %s" % fn)
            return

        makedirs(dirname(fn), exist_ok=True)

        with open(fn, 'w') as f:
            dump(item, f, **self.dump_config)
