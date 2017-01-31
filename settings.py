# -*- coding: utf-8 -*-

SPIDER_MODULES = (
    'dmm.spiders',
    'ave.spiders',
)

LOG_LEVEL = 'INFO'

USER_AGENT = 'scrapy-jav/0.5'
ROBOTSTXT_OBEY = True
COOKIES_ENABLED = False

EXTENSIONS = {
    'scrapy.extensions.telnet.TelnetConsole': None,
}

ARIA_DIR = '/media/downloads'
ARIA_RPC = 'http://localhost:6800/rpc'
ARIA_TOKEN = 'token:asdfghjkl'
