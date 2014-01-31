#!/usr/bin/env python

"""
Download full-text PDF files following link on CiteSeerX page

Usage:

$ ./download_fulltext.py ../crawl_citeseer/CiteSeerXSpider.xml docs

where results.xml is the result from the CiteSeerX crawl and 
docs is the directory for PDF files 
"""

import logging as log
from lxml import etree
from os import path
import requests
import subprocess
import urlparse


def download_fulltext(crawl_fname, out_dir, timeout=60):
    tree = etree.parse(crawl_fname)
    exist = succes = fail = 0
    
    for item in tree.findall("//item"):
        log.debug(78 * "-")        
        author = item.find("author").text
        log.debug(u"author = {}".format(author))
        url = item.find("url").text
        query = urlparse.urlparse(url).query
        doi = urlparse.parse_qs(query)["doi"][0]
        log.debug("doi = {}".format(doi))        
        out_fname = path.join(out_dir, doi + ".pdf")        
        downloaded = False
        
        if path.exists(out_fname):
            exist += 1
            log.debug("File {} already exists".format(out_fname))
            continue

        # try external download locations first to reduce load on CiteSeerX
        log.debug("Checking download links")
        for link in item.xpath("download_links/value/text()"):
            parse_result = urlparse.urlparse(link)
            if ( parse_result.scheme == "http" and 
                 parse_result.path[-4:].lower() == ".pdf"):
                log.debug("Trying download from {}".format(link))
                try:
                    # timeout seconds to establish connection and another
                    # timeout seconds to download - otherwise 
                    result = requests.get(link, timeout=timeout)
                except requests.RequestException as inst:
                    log.debug(inst)
                    continue
                if result.ok:
                    log.debug("Download succeeded")
                    content_type = result.headers["content-type"] 
                    if content_type == "application/pdf":
                        log.info("saving {}".format(out_fname))
                        open(out_fname, "wb").write(result.content)
                        succes += 1
                        downloaded = True
                        break
                    else:
                        log.debug("Unexpected content-type: {}".format(
                            content_type))
                else:
                    log.debug("Failure: {}".format(result.reason))
            else:
                log.debug("Cannot handle {}".format(link))
        else:
            log.debug("All download links failed")        
            
        if downloaded:
            continue

        log.debug("Checking cached links")
        
        # download from external locations failed, 
        # so try cached version on CiteSeerX
        for link in item.xpath("cached_links/value/text()"):
            parse_result = urlparse.urlparse(link)
            if "type=pdf" in parse_result.query:
                log.debug("Trying download from {}".format(link))
                result = requests.get(link)
                if result.ok:
                    log.debug("Download succeeded")
                    content_type = result.headers["content-type"] 
                    if content_type == "application/pdf":
                        log.info("saving {}".format(out_fname))
                        open(out_fname, "wb").write(result.content)
                        succes += 1
                        downloaded = True
                        break
                    else:
                        log.debug("Unexpected content-type: {}".format(
                            content_type))
                else:
                    log.debug("Failure: {}".format(result.reason))
            else:
                log.debug("Cannot handle {}".format(link))
        else:
            log.debug("All cached links failed")        
                
        if not downloaded:
            fail += 1
            log.error(u"No full-text download for author {} from {}".format(
                author, url))
            
    log.debug(78 * "-")                    
    log.debug("Succesfully downloaded: {}".format(succes))
    log.debug("Failed to downloaded: {}".format(fail))
    log.debug("Already existed: {}".format(exist))
    log.debug("Total: {}".format(succes + fail + exist))
    
        
        

if __name__ == "__main__":
    import sys
    log.basicConfig(level=log.DEBUG)
    download_fulltext(sys.argv[1], sys.argv[2])
    
