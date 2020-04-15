#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct  6 08:16:15 2017

@author: hcorrada
"""
import numpy as np
from collections import defaultdict
from plagiarism_lib.hashing import _make_hashes

# Invert shingled article dataset so we can iterate over shingles
#
# shingled_data: list of (docid, shingles) tuples
#    docid: document id 
#    shingles: set of 32-bit integers encoding document shingles of corresponding document
#
# returns: sorted list of tuples (s, docid):
#    s: 32-bit integer encoding document shingle
#    docid: id of document where s occurs
def invert_shingles(shingled_data):
    inv_index = []
    docids = []
    
    for (docid, shingles) in shingled_data:
        docids.append(docid)
        for s in shingles:
            item = (s, docid)
            inv_index.append(item)
    return sorted(inv_index), docids


# Create a minhash signature matrix
#
# shingled_data: a shingled article dataset, format depends on argument 'inverted' (see below)
# num_hashes: number of hash functions to use in the minhash summary
# inverted: boolean, is the shingled data already inverted (see below)
#
# returns: tuple (mh, docids) 
#   mh: a numpy matrix (num_hashes x num_docs) of minhash signature
#   docids: a list of document ids
# 
# note: if argument 'inverted' is True, then shingled data is already sorted by shingle, so
# the minhash algorithm can use directly. In this case, 'shingled_data' is assumed to be 
# a sorted list of (s, docid) tuples, with s a shingle, and docid a document id/
#
# If argument 'inverted' is False, then shingled data is organized by document and we need
# to create an inverted index so we can iterate by shingle. In this case 'shingled_data' is
# assumed to be a list of (docid, shingles) tuples with docid a document id and
# shingles a 'set' of shingles
def _make_minhash_sigmatrix(shingled_data, num_hashes, inverted=False):
    
    # invert the shingled data if necessary
    if inverted:
        inv_index, docids = shingled_data
    else:
        inv_index, docids = invert_shingles(shingled_data)
        
    # initialize the signature matrix with infinity in every entry
    num_docs = len(docids)
    sigmat = np.full([num_hashes, num_docs], np.inf)
    
    # create num_hashes random hash functions
    hash_funcs = _make_hashes(num_hashes)
    
    # avoid recomputing hash function values during iteration
    last_s = -1
    hashvals = []
    
    # iterate over shingles 
    for s, docid in inv_index:
        x = []
        print('s:', s) 
        print('docid:', docid)     
        ## print(inv_index) ##this and the two before are to check if they are ordered, runs out of space
        ##loop the rows, then the columns
        ##check if s is the same as it was before
        ##First thing. If you see a new shingle, compute the hash values, evaluate each one in hash_funcs with the value given in s
        ##List of hash values for one shingle
        ##Update when you see a new shingle
        ##Check for each document, is the value for that document and that hash value in the signature matrix smaller than the one
        ##just computed. If yes, do nothing, if no, update the signature matrix
        ##Other function that needs to be implemented. The one to compute similarity
        
            
        ## IMPLEMENT THIS LOOP!!!
        ##if we have already been through this shingle, skip it
        if s != last_s:
            hashvals.clear() ##this still contains the values from the prior shingle (possibly nothing if it's the first shingle)
            hashvals = [h(s) for h in hash_funcs] ##we know it works
            last_s = s ##need to set last_s to what it is now. s will retain is value until the end of this iteration of the loop
      

        for k in range(len(docids)):
            if docid == docids[k]:
                x.append(docids.index(docid)) ##this loop is to find and store the index of docid
        
        y = x[0] ##to put the index of docid in an acceptable format
        for j in range(num_hashes): ##will go through the rows
            if sigmat[j, y] == np.inf: ##the two if statements should adjust the columns accordingly
                sigmat[j, y] = hashvals[j]
            if hashvals[j] < sigmat[j, y]:
                sigmat[j, y] = hashvals[j]
                  
        x.clear() ##we need a different index for the next docid
        print(sigmat)
        
    return sigmat, docids


# Objects used to create and query minhash summaries
# Example using 10 hash functions:
#   mh = MinHash(10) 
#   mh.make_matrix(article_db)
#   mh.get_similarity(doci, docj)
class MinHash:
    # Construct an empty object that will use 'num_hashes' in the summary
    #
    # num_hashes: number of hashes to use in the 
    def __init__(self, num_hashes):
        self._num_hashes = num_hashes
        self._docids = None
        self._mat = None
        
    # Create the signature matrix
    # 
    # shingled_data: a shingled document dataset (see _make_minhash_sigmatrix)
    # inverted: is the dataset already inverted (see _make_minhash_sigmatrix)
    #
    # side effect: updates self._docids and self._mat atttributes of object
    def make_matrix(self, shingled_data, inverted=False):
        self._mat, self._docids = _make_minhash_sigmatrix(shingled_data,
                                                          self._num_hashes,
                                                          inverted=inverted)
        
    # compute minhash JS estimate for documents di and dj
    #
    # di: id of first document
    # dj: id of second document
    #
    # returns: minhash JS estimate (double)
    def get_similarity(self, di, dj):
        i = self._docids.index(di) ##docids position corresponding to id number di
        j = self._docids.index(dj) ##docids position corresponding to id number dj
        # FINISH IMPLEMENTING THIS!!!
        ## function to compute similarity
        ##with a minhash sigmatrix, estimate similarity by comparing 2 columns of sigmatrix, see how many elements match
        ##return proportion of those that match
        x = i
        y = j ##these two statements are to put the indexes of di and dj into an acceptable format
        
        s1 = []
        s2 = []
        for k in range(self._num_hashes):  ##this is to copy the columns into 2 separate lists  
            s1[k] = self._mat[k, x]
            s2[k] = self._mat[k, y]
   
        return (len(s1.intersection(s2))/len(s1.union(s2)))
    
    def save_matrix(self, file):
        np.save(file, self._mat)
        
    def from_file(self, docids, file):
        self._docids = docids
        self._mat = np.load(file).astype(np.int32)