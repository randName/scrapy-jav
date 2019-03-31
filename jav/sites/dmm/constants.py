DOMAIN = 'http://www.dmm.co.jp'

REALMS = (
    {'service': 'mono', 'shop': 'dvd'},
    {'service': 'digital', 'shop': 'videoa'}
)


def get_date_urls():
    base = (
        'calendar/=/year={0:%Y}/month={0:%m}/day={0:%d}-{1:%d}',
        'delivery-list/=/delivery_date={0:%Y-%m-%d}'
    )
    for r, b in zip(REALMS, base):
        yield '{0}/{service}/{shop}/-/{1}'.format(DOMAIN, b, **r)


DATE_URLS = tuple(get_date_urls())

DATE_MIN = (2001, 3, 1)

AIUEO = '//table[@class="menu_aiueo"]'

PAGEN = '(//div[contains(@class,"pagenation")])[1]'

RELATED = '%s/{0}/{1}/-/detail/=/cid={2}/' % DOMAIN

MUTUALS = '/misc/-/mutual-link/ajax-index/=/cid={0}/service={1}/shop={2}/'

ARTICLES = '%s/{service}/{shop}/-/list/=/article={article}/id={id}/' % DOMAIN

ARTICLE_LABELS = (
    'ジャンル',
    'シリーズ',
    'メーカー',
    'レーベル',
    '出演者',
    '監督',
)
