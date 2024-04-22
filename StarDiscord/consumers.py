from channels.generic.websocket import WebsocketConsumer
from channels.exceptions import StopConsumer
from users.user import User
import threading
import json
from environment import EnviromentBase
from utils.dataInfo import DataInfo
import time

class SocketVector():
    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.data = {}


    def getItems(self, keys) -> list:
        res = []
        with self.lock:
            for key in keys:
                if key in self.data.keys():
                    res.append(self.data[key])
        return res
    
    def getSocks(self) -> dict:
        res = {}
        with self.lock:
            for key, sock in self.data.items():
                res[key] = sock
        return res

    def setItem(self, key, sock):
        with self.lock:
            self.data[key] = sock
        
    def delItem(self, key):
        with self.lock:
            try:
                self.data[key].close()
            except Exception as e:
                pass
            del self.data[key]
    
    def delSock(self, sock):
        with self.lock:
            for k,s in self.data.items():
                if sock == s:
                    del self.data[k]
                    return
    
    def __str__(self) -> str:
        with self.lock:
            strTxt = str(self.data)
        return strTxt

class WebsockInfo(DataInfo):
    def __init__(self) -> None:
        pass


class ChatConsumer(WebsocketConsumer):
    sockets = SocketVector()
    def websocket_connect(self, message):
        self.accept()


    def websocket_receive(self, message):
        try:
            ChatConsumer.handlerMsg(self, json.loads(message["text"]))
        except Exception as e:
            print("ChatConsumer receive error:", e)


    def websocket_disconnect(self, message):
        try:
            self.getSockets().delSock(self)
        except Exception as e:
            print("ChatConsumer websocket_disconnect error:", e)
        raise StopConsumer()
    
    def getSockets(self):
        return ChatConsumer.sockets
    
    def sendData(self, webSocket:WebsockInfo):
        print("登陆响应：", webSocket)
        self.send(json.dumps(webSocket))

    # 处理接收的消息
    @staticmethod
    def handlerMsg(sock, message):
        print("登陆请求：", message)
        if "code" not in message.keys():
            return
        func = str(message["code"])
        th = threading.Thread(target=EnviromentBase.instance()[func], args=(sock, message))
        th.start()

    @staticmethod
    def pollEvent(sockets:SocketVector):
        while True:
            time.sleep(2)
            try:
                tmpSockets = sockets.getSocks()
                for userid, sock in tmpSockets.items():
                    try:
                        userMapper = User(_userid=int(userid))
                        caches = userMapper.getCaches()
                        for cache in caches:
                            try:
                                cache = dict(cache)
                                cache["code"] = 611001
                                sock.send(json.dumps(cache))
                            except Exception as ee:
                                print("ChatConsumer.pollEvent.ee:", ee)
                    except Exception as e:
                        print("ChatConsumer.pollEvent.e:", e)
            except Exception as em:
                print("ChatConsumer.pollEvent.em:", em)