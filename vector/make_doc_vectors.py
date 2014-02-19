#!/usr/bin/env python

"""
Create document vectors by vectorizing document.
Save matrix in Numpy and Marix Market format.
Save features and labels as text files.

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
from scipy.io import mmwrite

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
    
    log.info("saving matrix in Numpy format to " + out_fname)
    np.savez(out_fname, 
             vectorizer=vectorizer,
             vectors=vectors,
             labels=labels)
    
    base_fname = splitext(out_fname)[0]
    
    mm_fname = base_fname + ".mtx"
    log.info("saving matrix in Matrix Market format to " + mm_fname)
    mmwrite(mm_fname, vectors, "IDIScape document vectors", "integer")

    feat_fname = base_fname + "_features.txt"
    log.info("saving features to " + feat_fname)
    feat_names = vectorizer.get_feature_names() 
    open(feat_fname, "w", "utf8").write(u"\n".join(feat_names))
    
    label_fname = base_fname + "_labels.txt"
    log.info("saving labels to " + label_fname)
    open(label_fname, "w", "utf8").write(u"\n".join(labels))    

if __name__ == "__main__":
    from sys import argv
    
    log.basicConfig(level=log.INFO)
    make_doc_vectors(*argv[1:])