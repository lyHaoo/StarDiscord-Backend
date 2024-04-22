from users.user import User
from utils.dataInfo import DataInfo
import time
from StarDiscord.consumers import ChatConsumer
import json
from StarDiscord.wrappers import wsAuthentication
from users.channel import Channel

class Handler():
    def __init__(self) -> None:
        pass


    @staticmethod
    def handlerLogin(sock:ChatConsumer, message:dict):
        loginRes = User.login(message["email"], message["password"])
        dataInfo = DataInfo()
        dataInfo.setItem("code", 611003)
        dataInfo.setItem("date", int(time.time()*1000))
        if loginRes is None:
            dataInfo.setItem("status", 2)
            sock.sendData(dataInfo)
        else:
            dataInfo.setItem("status", 1)
            token = User.token({"userid":loginRes["userid"], "email": loginRes["email"], "timestamp":int(time.time() * 1000)})
            dataInfo.setItem("token", token)
            dataInfo.setItem("msgid", int(time.time() * 1000))
            dataInfo.setItem("userid", loginRes["userid"])
            dataInfo.setItem("username", loginRes["username"])
            dataInfo.setItem("email", loginRes["email"])
            dataInfo.setItem("headimage", loginRes["headimage"])
            dataInfo.setItem("birthday", loginRes["birthday"])
            dataInfo.setItem("gender", loginRes["gender"])
            dataInfo.setItem("signature", loginRes["signature"])
            dataInfo.setItem("date", int(time.time() * 1000))
            dataInfo.setItem("friends", loginRes["friends"])
            dataInfo.setItem("channels", loginRes["channels"])
            dataInfo.setItem("myself", loginRes["myself"])
            sock.getSockets().setItem(str(loginRes["userid"]), sock)
            sock.sendData(dataInfo)
    
    @wsAuthentication
    @staticmethod
    def handlerChat(sock:ChatConsumer, message:dict):
        fields = ["code", "date", "msgid", "token", "userid", "type", "id", "data"]
        for field in fields:
            if field not in message.keys():
                return
        senderid = message.get("userid")
        recvid = message.get("id")
        chatid = int(time.time() * 1000)
        data = dict(message.get("data"))
        print("handlerChat:", message)
        if int(message.get("type")) == 1:
            recvMapp = User(_userid=recvid)
            if not recvMapp.lookFriend(senderid):
                return
            # 处理聊天记录结构
            chatInfo = DataInfo()
            chatInfo.setItem("chatid", chatid)
            chatInfo.setItem("date", chatid)
            chatInfo.setItem("userid", recvid)
            chatInfo.setItem("sender", senderid)
            chatInfo.setItem("data", data)
            # 插入到发送者的聊天记录表
            chatInfo.setItem("type", 0)
            senderMapper = User(_userid=senderid)
            senderMapper.insertChat(chatInfo)
            # 插入到接收者的聊天记录表
            chatInfo.setItem("type", 1)
            recvMapper = User(_userid=recvid)
            recvMapper.insertChat(chatInfo)

            # 缓存待发送
            cacheInfo = DataInfo()
            cacheInfo.setItem("chatid", chatid)
            cacheInfo.setItem("date", chatid)
            cacheInfo.setItem("userid", recvid)
            cacheInfo.setItem("type", 1)
            cacheInfo.setItem("sender", senderid)
            cacheInfo.setItem("channelid", -1)
            cacheInfo.setItem("tag", "")
            cacheInfo.setItem("data", data)
            recvMapper.insertCache(cacheInfo)

        elif int(message.get("type")) == 2:
            channelid = message.get("id")
            channelMapper = Channel(channelid=channelid)
            channelMapper.insertChat(message)
        
    # 处理推送消息接收的响应
    def msgResponse(sock:ChatConsumer, message:dict):
        userid = int(message["userid"])
        chatid = int(message["chatid"])
        userMapper = User(_userid=userid)
        userMapper.delCache(chatid)