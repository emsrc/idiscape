#!/usr/bin/env python

"""
Create author vectors by summing the document vectors of their publications.
Save matrix in Numpy and Marix Market format.
Save labels as text file (features are the same as for document vectors).

Usage:

 ./make_author_vecs.py  ../crawl_idi/IDISpider.xml docvecs.npz authvecs.npz
"""

import logging as log
from lxml import etree
import urlparse
from os.path import splitext
from codecs import open

import numpy as np
import scipy.sparse as sp
from scipy.io import mmwrite


def make_author_vectors(crawl_fname, doc_vec_fname, auth_vec_fname):
    docs = np.load(doc_vec_fname)
    doc_vecs = docs["vectors"][()]
    # Convert to LIL, because modifying CSR is slow
    doc_vecs = doc_vecs.tolil()
    
    # Create mapping from label (=DOI) to row number (=doc vector)  
    doi2n = dict((l,i) for i,l in enumerate(docs["labels"]))
    
    # Collect authors         
    tree = etree.parse(crawl_fname)
    authors = np.array(list(set(tree.xpath("//author/text()"))))

    # Create empty author vectors
    shape = (len(authors), doc_vecs.shape[1])
    auth_vecs = sp.lil_matrix(shape)     
    
    # Create mapping from authors to row number (=author vector)
    auth2n = dict((a,i) for i,a in enumerate(authors))
    
    ## author to group mapping
    ##auth2group = {}
    
    # Fill author vectors by adding doc vectors 
    for item in tree.findall("//item"):
        author = item.find("author").text
        ##group = item.find("group")
        ##auth2group[author] = group
        url = item.find("url").text
        query = urlparse.urlparse(url).query
        doi = urlparse.parse_qs(query)["doi"][0]
        log.debug(u"DOI={} author={}".format(doi, author))
        
        try:
            auth_vecs[auth2n[author]] += doc_vecs[doi2n[doi]]
        except KeyError:
            log.warning(u"No document with DOI={} for author {}".format(
                doi, author))
            
    auth_vecs = auth_vecs.tocsr()
    
    ##group_labels = [auth2group[auth] for auth in authors]
           
    log.info("saving matrix in Numpy format to " + auth_vec_fname)
    np.savez(auth_vec_fname, 
             vectorizer=docs["vectorizer"],
             vectors=auth_vecs,
             author_labels=authors,
             ##group_labels=group_labels
             ) 
    
    base_fname = splitext(auth_vec_fname)[0]
    
    mm_fname = base_fname + ".mtx"
    log.info("saving matrix in Matrix Market format to " + mm_fname)
    mmwrite(mm_fname, auth_vecs, "IDIScape document vectors", "integer")
    
    label_fname = base_fname + "_labels.txt"
    log.info("saving labels to " + label_fname)
    open(label_fname, "w", "utf8").write(u"\n".join(authors))    
    

if __name__ == "__main__":
    from sys import argv
    
    log.basicConfig(level=log.INFO)
    make_author_vectors(*argv[1:])