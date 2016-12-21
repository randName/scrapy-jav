# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.

import scrapy

from urllib.parse import urljoin
from .. import *

def urlparams(**kwargs):
    return '/'.join('%s=%s' % i for i in kwargs.items())

def realm_urls(url, realm=None):
    if realm is None:
        realm = range(len(realms))
    return tuple('%s/%s/%s' % (domain, realms[r], url) for r in realm)

def get_realm(url):
    for r in range(len(realms)):
        if realms[r] in url: return r

def pagelist(links, selector='li', callback=None):
    for l in links.css('%s %s' % (selector, href)).extract():
        yield scrapy.Request(urljoin(domain, l), callback=callback)
