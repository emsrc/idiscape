#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Extract text from PDF files, skipping
- PDF files with more than 50 pages
- converted text consisting mainly of garbage
- converted text not containing the author name

Assumes command line tools 'pdfinfo' and 'pdftotext' are on shell PATH.

Usage:

$ ./extract_text.py ../crawl_citeseer/CiteSeerXSpider.xml ../download/docs text

where 'CiteSeerXSpider.xml' is the result of crawling CiteSeerX,
'docs' is the dir containing PDF files and
'text' is an existing dir for writing txt files 
"""

from glob import glob
import logging as log
from subprocess import check_output, call
from os.path import basename, splitext, join, exists
from os import remove
from codecs import open
from lxml import etree
from urlparse import parse_qs, urlparse
from tempfile import NamedTemporaryFile
import re

from unidecode import unidecode

remove_re = re.compile(u'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]')



def extract_text(crawl_fname, pdf_dir, txt_dir, max_pages=50):
          
    tree = etree.parse(crawl_fname)
    author_patterns = {}
    tmp_fname = NamedTemporaryFile().name
    
    for item in tree.findall("//item"):
        author = item.find("author").text
        url = item.find("url").text
        query = urlparse(url).query
        doi = parse_qs(query)["doi"][0]
        
        pdf_fname = join(pdf_dir, doi + ".pdf")
        
        if not exists(pdf_fname):
            log.info("{} does not exist".format(pdf_fname))
            continue
        
        n = pages(pdf_fname)
        
        if n > max_pages:
            log.warn("{} skipped because it has too many pages ({})".format(
            pdf_fname, n))
            continue        
        
        text =  pdf_to_text(pdf_fname, tmp_fname)
        
        if not text:
            log.error("conversion of {} to text failed".format(pdf_fname))
            continue
        
        if is_garbage(text):
            # For reasons yet unknown, pdftotext in some cases generates
            # complete garbage. Unfortunately Stanford CoreNLP chokes on such
            # files with mostly non-ascii chars (heap out of memory). Hence
            # these cases need to be filtered out.
            log.warn("skipping {} because text output is garbage".format(pdf_fname))
            continue
           
        # If a name contains non-ascii chars, e.g. "Pinar Õztürk", don't bother
        # looking for it in the text because pdftotext conversion most likely
        # messed up the name beyond recognition
        if author != unicode(unidecode(unicode(author))):
            log.info(u"skipping author name check for non-ascii name " + author)
        else:
            # Filter out documents that do not contain some variant of the author
            # name. This removes roughy half of the documents, mainly because of
            # a number of highly ambiguous names.
            author_pat = author_patterns.setdefault(author, 
                                                    compile_author_pattern(author))
            log.debug(u"{}: {} --> {}".format(pdf_fname, author, author_pat.pattern))
            
            limit = min(len(text)/2, 2500)
            result = author_pat.search(text[:limit])
            
            if result:
                log.debug(u"found " +  result.group())
            else:
                log.warn("skipping {} because author name not found".format(pdf_fname))
                continue    
            
        # Delete illegal XML chars, which break XML serialization in Stanford CoreNLP 
        text, n = remove_re.subn('', text)
        if n:
            log.debug("removed {} illegal XML chars".format(n))
            
        txt_fname = join(txt_dir, doi + ".txt")   
        log.debug("saving text to " + txt_fname)
        with open(txt_fname, "w", encoding="utf-8") as outf:
            outf.write(text)
            
            
                    
        
        
def pdf_to_text(pdf_fname, txt_fname): 
    """
    convert PDF tp plain text using 'pdftotext' command line tool
    """
    command = "pdftotext {} {}".format(pdf_fname, txt_fname)
    log.info(command)
    result = call(command, shell=True)
    if result == 0:
        return open(txt_fname, encoding="utf-8").read() 


def pages(fname):
    """
    return number of pages in pdf file according to 'pdfinfo' command line
    tool
    """
    command = "pdfinfo " + fname
    result = check_output(command, shell=True)
    return int([l.split()[1] for l in result.split("\n") 
                if l.startswith("Pages:")][0])


def is_garbage(text, threshold=0.75):
    """
    Determine if text contains English language or garbage by checking
    whether the the ratio between printable ascii chars and non-ascii chars
    exceeds the threshold
    """
    n_ascii_chars = len([c for c in text if 32 <= ord(c) <= 126])
    ratio = n_ascii_chars / float(len(text))
    is_garbage = ratio <= threshold
    if is_garbage:
        log.debug(text[:1000] + "\n.\n.\n.\n" + text[-1000:])
    return is_garbage

        
def compile_author_pattern(author):
    """
    compile regular expression for searching plausible variants of author name
    """
    # Construct a regular expression from the parts of a name (at least two).    
    parts = author.split()

    # First name is virtually always given enitirely
    pat = parts[0] + u"\\s+"
    
    # Check for middle names
    for midpart in parts[1:-1]:
        if midpart.endswith("."):
            # Initials such as "C" or "C."
            pat += u"(" + midpart.strip(".") + u"\\.\\s+)?"
        else:
            # In case of a full middle name, allow both full name and initial
            pat += u"(" + midpart + "\\s+|" + midpart[0] + u"\\.\\s+)?"
            
    if len(parts) == 2:
        # If no middle names are given, allow an optional initial,
        # e.g. for "Pauline Haddow" allow "Pauline C. Haddow" as well
        pat += u"([A-Z]\\.\\s+)?"
     
    # Add last name
    pat += parts[-1]
    
    return re.compile(pat, re.IGNORECASE|re.UNICODE)
    
        

    
if __name__ == "__main__":
    import sys
    log.basicConfig(level=log.DEBUG)
    extract_text(*sys.argv[1:])
    
            