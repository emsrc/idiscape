import codecs
import urlparse

from scrapy.contrib.spiders import CrawlSpider
from scrapy.selector import Selector
from scrapy.http import Request
from scrapy import log

import unidecode

from crawl_citeseer.items import CiteSeerXItem


class CiteSeerXSpider(CrawlSpider):

    name = 'CiteSeerX'
    allowed_domains = ['citeseer.ist.psu.edu']    
    domain = u'http://citeseer.ist.psu.edu'
    search_url = domain + '/search?q=author%3A({})'
    
    def start_requests(self):
        fname = self.settings.get("AUTHOR_NAMES_FILE")
        log.msg("reading author names from %s" % fname)
        with codecs.open(fname, encoding="utf-8") as f:
            for author in f:
                author = author.strip()
                if author:
                    url = self.create_search_url(author)
                    request = Request(url, callback=self.parse_result_list)
                    # pass on author to callback function via request's meta attrib
                    request.meta["author"] = author
                    yield request
                    
    def create_search_url(self, author):
        # Transliterate an Unicode object into closest ASCII string,
        # stripping diacritics and substituting closests ascii char,
        # because SiteCeerX can't handle them
        s = unidecode.unidecode(author)
        names = s.split()
        # Keep only first and last name, ignoring intermediate names,
        # as this seems to give best results with CiteSeerX
        terms = names[0] + "+" + names[-1]
        # create search query 
        return self.search_url.format(terms)

    def parse_result(self, response):
        sel = Selector(response)
        item = CiteSeerXItem()
        item["url"] = response.url
        item["author"] = response.meta["author"]
        abstract = sel.xpath('//div[@id="abstract"]/p/text()').extract()
        try:
            item["abstract"] = abstract.pop()
        except IndexError:
            pass
        bibtex_extract = sel.xpath('//div[@id="bibtex"]/p/text()').extract()
        item["bibtex"] = "\n".join(line.strip() for line in bibtex_extract)
        clinks = sel.xpath('//ul[@id="clinks"]/li/a/@href').extract()
        item["cached_links"] = [(self.domain + link) for link in clinks]
        item["download_links"] = sel.xpath('//ul[@id="dlinks"]/li/a/@href').extract()
        return item
    
    def parse_result_list(self, response):
        sel = Selector(response)
        result_urls = sel.xpath('//a[@class="remove doc_details"]/@href').extract()
        
        for url in result_urls:
            url = self.domain + url
            # However, some authors share the same papers and in that case
            # the same page must be crawled multiple times. By default,
            # Scrapy filters identical requests to avoid endless loops,
            # so we need the 'dont_filter' flag.
            request = Request(url, callback=self.parse_result, dont_filter=True)
            # pass on author to callback function via request's meta attrib
            request.meta["author"] = response.meta["author"]
            yield request
        
        next_urls = sel.xpath('//div[@id="pager"]/a/@href').extract()
        
        # follow only one of the "Next 10"" links
        if next_urls:
            url = self.domain + next_urls[0]
            request = Request(url, callback=self.parse_result_list)
            # pass on author to callback function via request's meta attrib
            request.meta["author"] = response.meta["author"]
            yield request
            