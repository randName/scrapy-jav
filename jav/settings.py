BOT_NAME = 'scrapy-jav'

SPIDER_MODULES = (
    'jav.sites.dmm.spiders',
    'jav.sites.ave.spiders',
)

LOG_LEVEL = 'INFO'

USER_AGENT = 'scrapy-jav/0.5'
ROBOTSTXT_OBEY = True
COOKIES_ENABLED = False

TELNETCONSOLE_ENABLED = False

EXTENSIONS = {
    'scrapy.extensions.telnet.TelnetConsole': None,
}

FEED_EXPORTERS = {
    'url': 'generics.exporters.UrlExporter',
}

SPIDER_MIDDLEWARES = {
    'jav.middlewares.NotFoundMiddleware': 75,
}

DOWNLOADER_MIDDLEWARES = {
    'jav.middlewares.XPathRetryMiddleware': 540,
}
