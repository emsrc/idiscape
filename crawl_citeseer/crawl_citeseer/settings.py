# Scrapy settings for crawl_citeseer project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'crawl_citeseer'

SPIDER_MODULES = ['crawl_citeseer.spiders']
NEWSPIDER_MODULE = 'crawl_citeseer.spiders'

ITEM_PIPELINES = {
    'crawl_citeseer.pipelines.ValidateItem': 300,
}

FEED_URI  = "%(name)s.xml"
FEED_FORMAT = "xml"

#LOG_FILE = "%(name)s_%(time)s.log"

CRAWL_IDI_FILE = "../crawl_idi/IDISpider.xml"

DOWNLOAD_DELAY = 1.0    # 1 sec of delay (on average)

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'crawl_citeseer (emarsi@idi.ntnu.no)'
