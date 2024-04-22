import threading


class AtomVector():
    def __init__(self) -> None:
        self.lock = threading.Lock()
        self._data = [(0,None),(0,None),(0,None),(0,None),(0,None),(0,None),(0,None),(0,None),(0,None),(0,None),(0,None),(0,None),(0,None),(0,None),(0,None),(0,None),(0,None),(0,None),(0,None),(0,None)]