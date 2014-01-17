#!/usr/bin/env python

"""
Extract text from PDF files

Assumes command line tools 'pdfinfo' and 'pdftotext' are on shell PATH.

Files with more than 50 pages are skipped.

Usage:

$ ./extract_text.py "../download/docs/*.pdf" text

where "../download/docs/*.pdf" is a quoted glob pattern and 'text' is an existing output dir. 
"""

from glob import glob
import logging as log
from subprocess import check_output, call
from os.path import basename, splitext, join
from os import remove
from codecs import open


def extract_text(fname_pat, out_dir, max_pages=50):
    for in_fname in glob(fname_pat):
        n = pages(in_fname)
        if n > max_pages:
            log.info("{} skipped because it has too many pages ({})".format(
            in_fname, n))
            continue
        out_fname = splitext(basename(in_fname))[0] + ".txt"
        out_fname = join(out_dir, out_fname)
        command = "pdftotext {} {}".format(in_fname, out_fname)
        log.info(command)
        result = call(command, shell=True)
        if result > 0:
            log.error("conversion failed for " + in_fname)
        elif is_garbage(out_fname):
            # For reasons yet unknown, pdftotext in some cases generates
            # complete garbage. Unfortunately Stanford CoreNLP chokes on such
            # files with mostly non-ascii chars (heap out of memory). Hence
            # these cases need to be filtered out.
            log.info("{} skipped because output is garbage".format(in_fname))
            remove(out_fname)    


def pages(fname):
    """
    return number of pages in pdf file according to 'pdfinfo' command line
    tool
    """
    command = "pdfinfo " + fname
    result = check_output(command, shell=True)
    return int([l.split()[1] for l in result.split("\n") 
                if l.startswith("Pages:")][0])


def is_garbage(fname, threshold=0.75):
    """
    Determine if named file contains English language or garbage by checking
    whether the the ratio between printable ascii chars and non-ascii chars
    exceeds the threshold
    """
    all_chars = open(fname, encoding="utf-8").read() 
    n_ascii_chars = len([c for c in all_chars if 32 <= ord(c) <= 126])
    ratio = n_ascii_chars / float(len(all_chars))
    is_garbage = ratio <= threshold
    if is_garbage:
        log.debug(all_chars[:1000] + "\n.\n.\n.\n" + all_chars[-1000:])
    return is_garbage
    


        
        

    
if __name__ == "__main__":
    import sys
    log.basicConfig(level=log.DEBUG)
    extract_text(*sys.argv[1:])
    
            