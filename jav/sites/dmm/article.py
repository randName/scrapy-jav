from .constants import PAGEN

performer_re = {
    'actress': r'.*\xa0(.+?)(?:[(（](.+?)[)）])?(?:\(([^)]+?)\))?$',
    'histrion': r'.*\xa0(.+?)(?:（(.+?)）)?(?:\(([^)]+?)\))?$',
}


def get_article(url, **article):
    for i in url.split('/'):
        try:
            k, v = i.split('=')
        except ValueError:
            continue

        if k == 'id':
            try:
                article['id'] = int(v)
            except ValueError:
                return None
        elif k == 'article':
            article['article'] = v

    return article


def save_article(urls):
    for url in urls:
        a = get_article(url)
        if a:
            yield '{article}:{id}'.format(**a)


def parse_article(response):
    item = response.meta.get('article') or get_article(response.url)
    if item is None:
        return

    span = response.xpath('string(//p[@class="headwithelem"]/span)')

    kana = None
    alias = None
    article = item['article']

    if article in performer_re:
        name, alias, kana = span.re(performer_re[article])
    elif article == 'director':
        name, kana = span.re(r'.*\xa0(.+?)(?:\(([^)]+?)\))?$')
    else:
        name = item.pop('name', span.re_first(r'.*\xa0(.+)$'))

    item['name'] = name

    if alias:
        item['alias'] = alias

    if kana:
        item['kana'] = kana

    ct = response.xpath(PAGEN).xpath('p/text()').re_first(r'([\d,]+)')
    if ct:
        item['count'] = int(ct.replace(',', ''))

    return item
