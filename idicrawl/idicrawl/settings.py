# Scrapy settings for idicrawl project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'idicrawl'

SPIDER_MODULES = ['idicrawl.spiders']
NEWSPIDER_MODULE = 'idicrawl.spiders'

ITEM_PIPELINES = {
    'idicrawl.pipelines.ValidateItem': 300,
}

FEED_URI  = "%(name)s_%(time)s.xml"
FEED_FORMAT = "xml"

#LOG_FILE = "%(name)s_%(time)s.log"

AUTHOR_NAMES_FILE = "author_names.txt"

DOWNLOAD_DELAY = 0.5    # 500 ms of delay (on average)

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'idicrawl (emarsi@idi.ntnu.no)'
