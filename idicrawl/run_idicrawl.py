"""
Call idicrawler from Python raher than through scrapy command line script.
This is for debugging with Wing.
"""

from twisted.internet import reactor
from scrapy.crawler import Crawler
from scrapy import log, signals
from scrapy.utils.project import get_project_settings
from idicrawl.spiders.citeseerx import CiteSeerXSpider

spider = CiteSeerXSpider()
settings = get_project_settings()
crawler = Crawler(settings)
crawler.signals.connect(reactor.stop, signal=signals.spider_closed)
crawler.configure()
crawler.crawl(spider)
crawler.start()
log.start(loglevel='DEBUG')
reactor.run() # the script will block here until the spider_closed signal was sent