"""
crawl http://www.idi.ntnu.no/ for info on scientific staff
"""

from scrapy.contrib.spiders import CrawlSpider
from scrapy.selector import Selector
from scrapy.http import Request
from scrapy import log

from crawl_idi.items import IdiItem



class IDISpider(CrawlSpider):

    name = 'IDISpider'
    allowed_domains = ['www.idi.ntnu.no']  
    start_urls = [
            "http://www.idi.ntnu.no/people/faculty.php",
            "http://www.idi.ntnu.no/people/researchers.php",
            "http://www.idi.ntnu.no/people/phd_students.php"]
    domain = "http://www.idi.ntnu.no"
    
    
    def parse(self, response):
        sel = Selector(response)
        item = IdiItem()
        
        for overview in sel.xpath('//div[@class="overview"]'):
            item["name"] = overview.xpath('span[@class="navn"]/b/a/text()').extract()[0]
            item["position"] = overview.xpath('span[@class="navn"]/text()').extract()[0]
            item["group"] = overview.xpath('table/tr/td/a/text()').extract()[0]
            url_path = overview.xpath('a/@href').extract()[0]
            item["url"] = self.domain + url_path
            img_path = overview.xpath('a/img/@src').extract()[0]
            item["img"] = self.domain + img_path
            yield item
            