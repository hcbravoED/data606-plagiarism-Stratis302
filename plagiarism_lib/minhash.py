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
            
        ## IMPLEMENT THIS LOOP!!!
            ##if we have already been through this shingle, skip it
            hashvals.clear()
            if s == last_s:
                last_s = s
            ##if we haven't been through this shingle yet, then put it through the hash functions, the hash values of this shingle in the
            ##hash functions are placed in the list hashvals[]
            else:
                for i in range(num_hashes):
                    #current_hash = hash_funcs[i]#is this necessary?
                    hashvals = [h(s) for h in hash_funcs]
                    last_s = s
                
                ##put the hashvals in sigmatrix, if necessary
                for i in range(num_docs):
                    if docid == docids[i]:
                        for j in range(num_hashes):
                            if sigmat[j, i] == np.inf:
                                sigmat[j, i] = hashvals[j]
                            if hashvals[j] < sigmat[j, i]:
                                sigmat[j, i] = hashvals[j]
            
        ##shingled_data is a list of all shingles, with all documents they appear in. Characteristic matrix
        ##loop through input, have shingles and id of document it appeared in. You see all tuples for a given shingle in a row.
        ##sigmat is the sigma matrix
        ##this is essentially the first 2 loops of the pseudocode
        ##pseudocode iterates over shingles. then loop through the columns
        ##the loop iterates over those pairs
        ##this loop essentially corresponds to the bottom of the screenshot
        ##it's a particular shingle, it's a document in which the shingle occurs
        ##check, for each hash value, if you need to update the matrix
        
        ##if you see a new shingle, compute its hash values, this is what hash_funcs is, a list of hash functions
        ##evaluate all hash functions in hash_funcs with the value given in s. Gives a list of hash values for that shingle
        ##every time you see a new shingle, update hash_vals
        ##for each document you check in order for each of the hash values, is the current value for that document and that hash function
        ##currently in the signature matrix smaller than the value just computed. If it is, it becomes the new value for that signature 
        ##matrix. If not, do nothing
        
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
        i = self._docids.index(di)
        j = self._docids.index(dj)
        # FINISH IMPLEMENTING THIS!!!
        ## function to compute similarity
        ##with a minhash sigmatrix, estimate similarity by comparing 2 columns of sigmatrix, see how many match
        ##return proportion of those that match
        l = 0
        for k in range(self._num_hashes):
            if self._mat[k][i] == self._mat[k][j]:
                l = l+1

        return (l/self._num_hashes)
    
    def save_matrix(self, file):
        np.save(file, self._mat)
        
    def from_file(self, docids, file):
        self._docids = docids
        self._mat = np.load(file).astype(np.int32)