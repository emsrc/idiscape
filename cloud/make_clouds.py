#!/usr/bin/env python

"""
Generate word clouds for all authors

Usage:

    $ ./make_clouds.py ../vector/authvecs.npz  img

where 'img' is the output directory for png files.

"""

import numpy as np
from os.path import join
import logging as log

from wordcloud import make_wordcloud



def make_clouds(auth_vec_fname, out_dir="img", max_words=200):
    arch = np.load(auth_vec_fname)
    authors = arch["author_labels"]
    vectorizer = arch["vectorizer"][()]
    vectors = arch["vectors"][()]
    
    vocab = np.array(vectorizer.get_feature_names())

    
    for author, vec in zip(authors, vectors):
        counts = vec.toarray().ravel()  
        
        if counts.sum() > max_words:
            mask_inds = counts.argsort()[-max_words:]
            counts = counts[mask_inds]
            words = vocab[mask_inds]
        else:
            log.error(u"vector for author {} has not enough words ({})".format(
                author, int(counts.sum())))
            continue
        
        out_fname = join(out_dir, author + ".png")
        log.debug(u"writing " + out_fname)
        
        make_wordcloud(words, counts, out_fname,
        font_path="/usr/local/texlive/2012/texmf-dist/fonts/truetype/public/droid/DroidSansMono.ttf",
        width=1000, height=600, show_img=False)

    
    
    
if __name__ == "__main__":
    from sys import argv
    log.basicConfig(level=log.DEBUG)
    make_clouds(*argv[1:])