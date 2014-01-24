# Scrapy settings for crawl_idi project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'crawl_idi'

SPIDER_MODULES = ['crawl_idi.spiders']
NEWSPIDER_MODULE = 'crawl_idi.spiders'


ITEM_PIPELINES = {
    'crawl_idi.pipelines.IdiImagePipeline': 200}

IMG_DIR = "img"


FEED_EXPORTERS = {
    'sqlite': 'crawl_idi.pipelines.SqliteItemExporter',
}

FEED_URI  = "%(name)s_%(time)s.db"
FEED_FORMAT = "sqlite"


# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'crawl_idi (emars@idi.ntnu.no)'