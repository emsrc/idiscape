#!/usr/bin/env python

"""
Generate word clouds for all authors

Usage:

    $ ./make_clouds.py ../vector/authvecs.npz  ../crawl_idi/IDISpider.xml img

where 'img' is the output directory for png files.

"""

import numpy as np
from os.path import join, basename, splitext
import logging as log
from lxml import etree

from wordcloud import make_wordcloud



def make_clouds(auth_vec_fname, crawl_fname, out_dir="img", max_words=200):
    arch = np.load(auth_vec_fname)
    labels = arch["author_labels"]
    vectorizer = arch["vectorizer"][()]
    vectors = arch["vectors"][()]
    
    # get author'a ascii name (as used for IDI photo)         
    tree = etree.parse(crawl_fname)
    authors = [unicode(e) 
               for e in tree.xpath("//name/text()")]
    ascii_name= [splitext(basename(e))[0]
                 for e in tree.xpath("//img/text()")]
    toascii = dict(zip(authors, ascii_name))
    
    vocab = np.array(vectorizer.get_feature_names())

    
    for author, vec in zip(labels, vectors):
        counts = vec.toarray().ravel()  
        
        if counts.sum() > max_words:
            mask_inds = counts.argsort()[-max_words:]
            counts = counts[mask_inds]
            words = vocab[mask_inds]
        else:
            log.error(u"vector for author {} has not enough words ({})".format(
                author, int(counts.sum())))
            continue
        
        out_fname = join(out_dir, toascii[author] + ".png")
        log.debug(u"writing " + out_fname)
        
        make_wordcloud(words, counts, out_fname,
        #font_path="/usr/local/texlive/2012/texmf-dist/fonts/truetype/public/droid/DroidSansMono.ttf",
        font_path="/usr/local/texlive/2012/texmf-dist/fonts/truetype/public/opensans/OpenSans-Regular.ttf",
        width=1000, height=600, show_img=False)

    
    
    
if __name__ == "__main__":
    from sys import argv
    log.basicConfig(level=log.DEBUG)
    make_clouds(*argv[1:])