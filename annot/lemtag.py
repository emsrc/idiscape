#!/usr/bin/env python

"""
Extract lemma (and optionally POS tag) from XML output by Stanford CoreNLP

Usage:

$ ./lemtag.py "xml/*.xml" lemtag

where "xml/*.xml" is a quoted glob pattern and 'lemtag' is an existing 
output dir. 
"""

from lxml import etree
from codecs import open
import logging as log


def lemtag(in_fname, out_fname, with_pos=False):
    log.info("writing to " + out_fname)
    outf = open(out_fname, "wb", encoding="utf-8")
    
    context = etree.iterparse(in_fname)
    for action, elem in context:
        if elem.tag == "lemma":
            outf.write(elem.text)
        elif elem.tag == "POS":
            if with_pos:
                outf.write("/" + elem.text + "\n")
            else:
                outf.write("\n")
        
if __name__ == "__main__":
    from sys import argv
    from glob import glob
    from os.path import splitext, basename, join
    
    log.basicConfig(level=log.DEBUG)
    
    for in_fname in glob(argv[1]):
        out_fname = splitext(basename(in_fname))[0] + ".lemtag"
        out_fname = join(argv[2], out_fname)
        lemtag(in_fname, out_fname)
    
    