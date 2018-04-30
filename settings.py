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
