import logger

logger.pushTimer()

from collections.abc import Callable, Iterable
import json
import os
import pickle
import ijson


class CachedObj:
    def __init__(self, file: str, calculator: Callable[[], object], mode:str='bytes'):
        self.file = f"cache/{file}"
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
            self.obj = self.calculator()
            self.serialize()
            logger.log("done")
            return True
        return False

    def clear(self):
        if os.path.exists(self.file):
            os.remove(self.file)


class CachedIter:
    def __init__(self, file: str, calculator: Callable[[], object], mode:str='bytes'):
        self.file = f"cache/{file}"
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
            self.serialize()
            logger.log("done")
            return True
        return False

    def clear(self):
        if os.path.exists(self.file):
            os.remove(self.file)

#TODO: use database
metadata_file = open('dre.json', 'rb')
def metadata() -> Iterable[tuple[int,str]]:
    metadata_file.seek(0)
    return ((m['id'], m['notes']) for m in ijson.items(metadata_file, 'item'))


def get_body(id: int):  #TODO
    for i,m in metadata():
        if i == id:
            return m

    

logger.log(f"archivist loaded. {logger.popTimer()} elapsed")