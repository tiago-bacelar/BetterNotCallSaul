import sqlite3
from bs4 import BeautifulSoup as BS
import multiprocessing
import re

from gensim.models import Word2Vec

splitter = re.compile(r'(\s|\t|\\n|,|\.|\"|\'|\?|!|;|:|»|«|\(|\)|\\|/)')
word = re.compile(r'\b(?:[^\W\d_]+(?:-[^\W\d_]+)*|\d+)\b',re.UNICODE)\



cores = multiprocessing.cpu_count()


w2v_model = Word2Vec(min_count=5,
                        max_vocab_size=None,
                        workers=cores-1)

def html2Text(text):
    txt = BS(text,'html.parser').get_text()
    if len(txt)>100000:
        return ""
    if len(txt)<5:
        return ""
    else:
        return txt

def getFirstElem(tup):
    return tup[0]


class Data():
    def __iter__(self):
        self.conn = sqlite3.connect("a.db")
        self.cur = self.conn.cursor()
        self.continuing = True
        self.rowsPerIt = 100000
        self.it=0
        self.currCache=[]
        return self

    def __next__(self):
        if self.currCache == []:
            if self.continuing == False:
                self.conn.close()
                raise StopIteration
            else:
                self.cur.execute(f'select text_content from dreapp_documenttext LIMIT {self.rowsPerIt} OFFSET {self.it*self.rowsPerIt}')
                self.it+=1
                print(self.it*self.rowsPerIt)
                self.currCache = self.cur.fetchall()
                if len(self.currCache)<self.rowsPerIt: self.continuing=False
        d=list(map(lambda x:x.lower(),re.findall(word,html2Text(getFirstElem(self.currCache.pop())))))
        #d = re.split(splitter,html2Text(getFirstElem(self.currCache.pop())))
        #d = list(map(lambda x:x.lower(),filter(lambda x: x not in ['-',' ','','\n',',','.','\"','\'','?','!',';',':','(',')','«','»','\\','/'] and not x.isnumeric(),d)))
        return d

data = Data()
print("building")
w2v_model.build_vocab(data)
print("training")
w2v_model.train(data, total_examples=w2v_model.corpus_count, epochs=5, report_delay=1)
print("saving")
w2v_model.save("model.model")
