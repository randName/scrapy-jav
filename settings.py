# -*- coding: utf-8 -*-

SPIDER_MODULES = ['dmm.spiders']
LOG_LEVEL = 'INFO'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'scrapy-jav/0.5'

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Enable or disable extensions
# See http://scrapy.readthedocs.org/en/latest/topics/extensions.html
EXTENSIONS = {
    'scrapy.extensions.telnet.TelnetConsole': None,
}
