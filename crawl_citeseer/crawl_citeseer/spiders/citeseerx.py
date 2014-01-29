import codecs
import urlparse
from lxml import etree

from scrapy.contrib.spiders import CrawlSpider
from scrapy.selector import Selector
from scrapy.http import Request
from scrapy import log

import unidecode

from crawl_citeseer.items import CiteSeerXItem


class CiteSeerXSpider(CrawlSpider):

    name = 'CiteSeerXSpider'
    allowed_domains = ['citeseer.ist.psu.edu']    
    domain = u'http://citeseer.ist.psu.edu'
    search_url = domain + '/search?q=author%3A({})'
    
    def start_requests(self):
        fname = self.settings.get("CRAWL_IDI_FILE")
        log.msg("reading author names from %s" % fname)
        tree = etree.parse(fname)
        for author in tree.xpath("//name/text()"):
            author = unicode(author)
            url = self.create_search_url(author)
            request = Request(url, callback=self.handle_query_response)
            # pass on author to callback function via request's meta attrib
            request.meta["author"] = author
            request.meta["use_initial"] = False
            yield request
                    
    def create_search_url(self, author, use_initial=False):
        # Transliterate an Unicode object into closest ASCII string,
        # stripping diacritics and substituting closests ascii char,
        # because SiteCeerX can't handle them
        s = unidecode.unidecode(author)
        names = s.split()
        if use_initial:
            # Use initial, as recommended by CiteSeerX, and last name,
            # ignoring intermediate names
            terms = names[0][0] + "+" + names[-1]    
        else:
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
    
    
    def handle_query_response(self, response):
        sel = Selector(response)
        author = response.meta["author"]
        use_initial = response.meta["use_initial"]
        
        # Did search query match any documents?        
        if sel.xpath('//div[@class="error"]'):
            self.log(u'Search for "author:({})" did not match any documents'.format(author))
            if not use_initial:
                # Create new request using first name initial
                self.log("Retrying search with first initial")
                url = self.create_search_url(author, use_initial=True)
                request = Request(url, callback=self.handle_query_response)
                # pass on author to callback function via request's meta attrib
                request.meta["author"] = author
                request.meta["use_initial"] = True
                yield request
        else:
            # Parse results
            result_urls = sel.xpath('//a[@class="remove doc_details"]/@href').extract()
            
            for url in result_urls:
                url = self.domain + url
                # However, some authors share the same papers and in that case
                # the same page must be crawled multiple times. By default,
                # Scrapy filters identical requests to avoid endless loops,
                # so we need the 'dont_filter' flag.
                request = Request(url, callback=self.parse_result,
                                  dont_filter=True)
                # pass on author to callback function via request's meta attrib
                request.meta["author"] = author
                yield request
            
            # Extract links to more results
            next_urls = sel.xpath('//div[@id="pager"]/a/@href').extract()
            
            # Follow only one of the "Next 10"" links
            if next_urls:
                url = self.domain + next_urls[0]
                request = Request(url, callback=self.handle_query_response)
                # pass on author to callback function via request's meta attrib
                request.meta["author"] = author                
                request.meta["use_initial"] = use_initial                
                yield request
            