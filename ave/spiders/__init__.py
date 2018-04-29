# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.

pagen = '(//div[@class="pagination"])[1]'

path_bases = {
    'subdept': 'keyword',
    'Actress': 'actress',
    'studio': 'studio',
}


def article_type(path):
    p = path[1:]

    for frag, cat in path_bases.items():
        if p.startswith(frag):
            return cat

    return None
