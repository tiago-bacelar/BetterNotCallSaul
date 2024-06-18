import logger

logger.pushTimer()

from collections.abc import Callable, Iterable
import json
import os
import pickle
import ijson
import sqlite3
from bs4 import BeautifulSoup as BS
from gensim.models import Word2Vec
import os

CURRFOLDER,_ = os.path.split(__file__)


class CachedObj:
    def __init__(self, file: str, calculator: Callable[[], object], mode:str='bytes'):
        self.file = os.path.join(CURRFOLDER,"cache",file)
        print(self.file)
        self.calculator = calculator
        self.mode = mode
        self.obj = None

    def serialize(self):
        if self.mode == 'bytes':
            with open(self.file, "wb") as f:
                pickle.dump(self.obj, f)
        elif self.mode == 'json':
            with open(self.file, "w") as f:
                json.dump(self.obj, f)

    def deserialize(self):
        if self.mode == 'bytes':
            with open(self.file, "rb") as f:
                self.obj = pickle.load(f)
        elif self.mode == 'json':
            with open(self.file, "r") as f:
                self.obj = json.load(f)


    def get(self) -> object:
        if self.obj is None:
            if not self.calculate():
                self.deserialize()
        return self.obj


    def calculate(self) -> bool:
        if not os.path.exists(self.file):
            logger.log(f"'{self.file}' not found. Generating...")
            logger.pushTimer()
            self.obj = self.calculator()
            self.serialize()
            logger.log(f"done. {logger.popTimer()}s elapsed")
            return True
        return False

    def clear(self):
        if os.path.exists(self.file):
            os.remove(self.file)


class CachedIter:
    def __init__(self, file: str, calculator: Callable[[], object], mode:str='bytes'):
        self.file = os.path.join(CURRFOLDER,"cache",file)
        self.calculator = calculator
        self.mode = mode

    def serialize(self):
        if self.mode == 'bytes':
            with open(self.file, "wb") as f:
                for obj in self.calculator():
                    pickle.dump(obj, f)
        elif self.mode == 'json':
            with open(self.file, "w") as f:
                json.dump(self.calculator(), f)

    def deserialize(self):
        if self.mode == 'bytes':
            with open(self.file, "rb") as f:
                while True:
                    try:
                        yield pickle.load(f)
                    except:
                        return
        elif self.mode == 'json':
            with open(self.file, "r") as f:
                yield from ijson.items(f, 'item')

    def get(self) -> object:
        self.calculate()
        return self.deserialize()
    
    def calculate(self) -> bool:
        if not os.path.exists(self.file):
            logger.log(f"'{self.file}' not found. Generating...")
            logger.pushTimer()
            self.serialize()
            logger.log(f"done. {logger.popTimer()}s elapsed")
            return True
        return False

    def clear(self):
        if os.path.exists(self.file):
            os.remove(self.file)

meta = None
DRE = os.path.join(CURRFOLDER,"model","dre.json")

def metadata() -> Iterable[tuple[int,str]]:
    #with open(os.path.join(CURRFOLDER,"model","dre.json"), 'rb') as f:
    #    yield from ((m['id'], m['notes']) for m in ijson.items(f, 'item'))
    global meta
    if meta == None:
        with open(DRE, 'rb') as f:
            meta = {m['id']: m['notes'] for m in ijson.items(f, 'item')}
    return meta.items()

def get_metadata(id: int) -> str:
    global meta
    if meta == None:
        with open(DRE, 'rb') as f:
            meta = {m['id']: m['notes'] for m in ijson.items(f, 'item')}
    return meta[id]

dbConn = sqlite3.connect(os.path.join(CURRFOLDER,"model","a.db"))
dbCur = dbConn.cursor()

def get_body(id: int):
    dbCur.execute(f'select text_content from dreapp_documenttext WHERE documenttext_id={id}')
    data = dbCur.fetchall()
    if data==[]:
        return "" #TODO:: Maybe change this
    else:
        return BS(data[0][0],'html.parser').get_text()

    

logger.log(f"archivist loaded. {logger.popTimer()} elapsed")