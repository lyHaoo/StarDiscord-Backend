import threading
import inspect

class EnviromentBase():
    _instance_lock = threading.Lock()
    def __new__(cls):
        pass

    @classmethod
    def instance(cls,*args, **kwargs):
        if not hasattr(EnviromentBase, '_instance'):
            with EnviromentBase._instance_lock:
                if not hasattr(EnviromentBase, '_instance'):
                    EnviromentBase._instance = object.__new__(cls, *args, **kwargs)
                    EnviromentBase._instance.__init__()
        return EnviromentBase._instance
    
    def __init__(self) -> None:
        pass
    
    def registerFunction(self, _func, _name):
        setattr(self, _name, _func)

    def __getitem__(self, key:str):
        return getattr(self, key)
    
    def __str__(self) -> str:
        methods = [m for m in dir(self) if inspect.ismethod(getattr(self, m)) and not m.startswith("__") and not m.endswith("__")][2:]
        return str(methods)