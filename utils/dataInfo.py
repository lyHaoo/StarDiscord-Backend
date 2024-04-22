from abc import abstractmethod
import json

class DataInfo(dict):
    def __init__(self) -> None:
        pass

    def get(self, key):
        return self[key]
    
    def keys(self):
        return [key for key in dict.keys(self)]
    
    def values(self):
        return [value for value in dict.values(self)]
    
    def setItem(self, key, value):
        self[key] = value
        # if isinstance(value, dict) or isinstance(value, list):
        #     self[key] = json.loads(value)
        # else:
        #     self[key] = value

    @abstractmethod
    def getTable(self):
        pass