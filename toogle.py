import itertools
import logger

logger.pushTimer()

from collections import Counter
from math import log2
from typing import Callable, Iterable
from gensim.models import Word2Vec
from archivist import CachedIter, CachedObj, metadata
#import nltk
from functools import reduce
import re
import pickle
import numpy as np
import json
import os


token_regex = re.compile(r'\b(?:[^\W\d_]+(?:-[^\W\d_]+)*|\d+)\b',re.UNICODE)
def tokenize(text: str) -> list[str]:
    return [t.lower() for t in re.findall(token_regex,text)]


w2v_model = Word2Vec.load('model/model.model')
def word2vec(token: str):
    if token in w2v_model.wv:
        return w2v_model.wv[token]

def word2norm(token: str):
    if token in w2v_model.wv:
        return w2v_model.get_vector(token, norm=True)

def zero():
    return [0 for _ in range(w2v_model.vector_size)]

#stopwords = nltk.corpus.stopwords.words('portuguese')
#TODO: remove stopwords?
#TODO: take the norm first?
def doc2vec(doc: str):
    tokens = [w2v_model.wv[s] for s in tokenize(doc) if s in w2v_model.wv]
    return np.mean(tokens, axis=0).tolist() if len(tokens) > 0 else zero()



def process_document(doc):
    tokens = tokenize(doc)
    return (len(tokens), Counter(tokens))

def cflat(counter):
    for x in counter:
        counter[x] = 1

def csum(counters):
    ans = Counter()
    for c in counters:
        cflat(c)
        ans.update(c)
    return ans

corpus_size = CachedObj('corpus_size.json', lambda: sum(1 for _ in metadata()), 'json')
#documents = CachedObj('documents.pickle', lambda: { id: process_document(txt) for id,txt in metadata() }, 'bytes')
document_frequencies = CachedObj('df.pickle', lambda: csum(Counter(tokenize(txt)) for _,txt in metadata()))

#TODO: precompute these in the cached files
#def tf(token, doc_id):
#    l, freq = documents.get()[doc_id]
#    return log2(1 + freq[token] / l) #TODO: switch to most frequent words?

def idf(token):
    return log2(corpus_size.get() / document_frequencies.get()[token])


avg_vecs = CachedIter('avg_vecs.pickle', lambda:((id,doc2vec(txt)) for id,txt in metadata()))


def collect(iters):
    ans = {}
    for g in iters:
        for k,v in g:
            if k in ans:
                ans[k].update(v)
            else:
                ans[k] = Counter(v)
    return ans

class TopN:
    def __init__(self, n: int, key: Callable):
        self.n = n
        self.key = key
        self.objs = []

    def add(self, o: object):
        order = self.key(o)
        if len(self.objs) < self.n:
            self.objs.append((o, order))
        else:
            m = min(order, *(v for _,v in self.objs))
            if m != order:
                for i in range(self.n):
                    if self.objs[i][1] == m:
                        self.objs[i] = (o, order)
                        break

    def get(self):
        return (o for o,_ in self.objs)

occurences = CachedIter('occurences.pickle', lambda:collect(((t,{id:n}) for t,n in Counter(tokenize(txt)).items() if t in w2v_model.wv and re.match(r"-?\d+",t) == None) for id,txt in metadata()).items())
doc_sizes = CachedObj('sizes.pickle', lambda:{id:len(tokenize(txt)) for id,txt in metadata()})

def similarity(t1, t2):
    w1 = w2v_model.wv[t1]
    w2 = w2v_model.wv[t2]
    return np.inner(w1,w2) / (np.linalg.norm(w1) * np.linalg.norm(w2)) #TODO: abs?

alpha = 5

#Given a query, returns all of the items in the dre, sorted from most to least relevant
def toogle(query: str) -> Iterable[int]:
    tops = {t:TopN(100, lambda o:o[2]) for t in tokenize(query)}
    
    for w,occ in occurences.get():
        for t,top in tops.items():
            top.add((w,occ,similarity(w,t)))

    scores = {}

    for t,top in tops.items():
        for w,occ,sim in top.get():
            for id,n in occ.items():
                scores[id] = scores.get(id, 0) + pow(2, alpha * (sim - 1)) * log2(1+n/doc_sizes.get()[id]) * idf(w)
 
    return sorted(scores.items(), key=lambda kv: kv[1],reverse=True)
    
    #aux = doc2vec(query)
    #return (id for id,_ in sorted(((id,np.inner(aux, vec)) for id,vec in avg_vecs.get()), key=lambda kv: kv[1], reverse=True))


logger.log(f"toogle loaded. {logger.popTimer()} elapsed")