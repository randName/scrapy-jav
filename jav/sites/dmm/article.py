performer_re = {
    'actress': r'.*\xa0(.+?)(?:[(（](.+?)[)）])?(?:\(([^)]+?)\))?$',
    'histrion': r'.*\xa0(.+?)(?:（(.+?)）)?(?:\(([^)]+?)\))?$',
}


def get_article(url, **article):
    u = url.split('/')[:-1]
    try:
        article['service'], article['shop'] = u[-7:-5]
        article['article'], aid = (v.split('=')[1] for v in u[-2:])
        article['id'] = int(aid)
    except (ValueError, IndexError):
        return None

    return article


def save_article(urls):
    for url in urls:
        a = get_article(url)
        if a:
            yield '{service}/{shop}/{article}/{id}'.format(**a)


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

    return item
