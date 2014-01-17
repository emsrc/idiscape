#!/usr/bin/env python

"""
Create document vectors by vectorizing document

Usage:

 ./make_doc_vectors.py  "../annot/lemtag/*.lemtag" docvecs
"""


import logging as log
from glob import glob
from os.path import splitext, basename, join
from codecs import open

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.stop_words import ENGLISH_STOP_WORDS
import numpy as np

# ignore special lemmas for round bracket and square bracket
OTHER_STOPWORDS = ["lrb", "rrb", "lsb", "rsb", "lcb", "rcb"]

def make_doc_vectors(fname_pat, out_fname):
    fnames = glob(fname_pat)
    labels = [splitext(basename(fn))[0] for fn in fnames]
    stop_words = frozenset(list(ENGLISH_STOP_WORDS) + OTHER_STOPWORDS)
    vectorizer = CountVectorizer(input="filename", 
                                 ngram_range=(1,3),
                                 min_df=5, 
                                 max_df=0.7,
                                 stop_words=stop_words,
                                 token_pattern=r"(?u)\b[A-Za-z]\w+\b")
    vectors = vectorizer.fit_transform(fnames)
    np.savez(out_fname, 
             vectorizer=vectorizer,
             vectors=vectors,
             labels=labels)



if __name__ == "__main__":
    from sys import argv
    
    log.basicConfig(level=log.DEBUG)
    make_doc_vectors(*argv[1:])