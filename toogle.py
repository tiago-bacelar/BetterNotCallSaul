import logger

logger.pushTimer()

from collections import Counter
from math import log2
from typing import Callable, Iterable
from gensim.models import Word2Vec
from archivist import CachedIter, CachedObj, metadata
#import nltk
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




def flatten_counter(counter):
    return Counter({k: 1 for k in counter})






def process_document(doc):
    tokens = tokenize(doc)
    return (len(tokens), Counter(tokens))

corpus_size = CachedObj('corpus_size.json', lambda: sum(1 for _ in metadata()), 'json')
documents = CachedObj('documents', lambda: { id: process_document(txt) for id,txt in metadata() }, 'bytes')
document_frequencies = CachedObj('df.json', lambda: sum((flatten_counter(freq) for _,freq in documents.get().values()), Counter()))

#TODO: precompute these in the cached files
def tf(token, doc_id):
    l, freq = documents.get()[doc_id]
    return log2(1 + freq[token] / l) #TODO: switch to most frequent words?

def idf(token):
    return log2(corpus_size.get() / document_frequencies.get()[token])


def tfidf(token, doc_id):
    return tf(token, doc_id) * idf(token)


avg_vecs = CachedIter('avg_vecs', lambda:((id,doc2vec(txt)) for id,txt in metadata()))


#Given a query, returns all of the items in the dre, sorted from most to least relevant
def toogle(query: str) -> Iterable[int]:
    aux = doc2vec(query)
    return (id for id,_ in sorted(((id,np.inner(aux, vec)) for id,vec in avg_vecs.get()), key=lambda kv: kv[1], reverse=True))


logger.log(f"toogle loaded. {logger.popTimer()} elapsed")