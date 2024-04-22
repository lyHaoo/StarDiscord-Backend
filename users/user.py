from users.userInfo import UserInfo
from utils.dbMysql import DBMysql
import time
from config.config import userFields, rsa
import hashlib
import base64
import json
from users.channel import Channel
from utils.dataInfo import DataInfo

class User(UserInfo):
    def __init__(self, _userid:int=None, _email:str=None) -> None:
        self.dbSql = DBMysql()
        self.initUser(_userid, _email)

    def initUser(self, _userid:int=None, _email:str=None):
        jsonFields = ["friends", "channels", "myself"]
        if _userid is not None:
            fields, values = self.dbSql.queryData("users", {"userid":_userid})
        elif _email is not None:
            fields, values = self.dbSql.queryData("users", {"email":_email})

        if fields is not None and values is not None and len(values) > 0:
            values = values[0]
            for index, value in enumerate(values):
                self[fields[index]] = json.loads(value) if fields[index] in jsonFields else value

    # 创建社区
    def newChannel(self,channelName:str):
        channelMapper = Channel.create(channelName=channelName, userid=int(self['userid']))
        if channelMapper is None:
            return None
        self["channels"][str(channelMapper["channelid"])] = {"channelid":channelMapper["channelid"], "channelname":channelMapper["channelname"], "userid":channelMapper["userid"]}
        self.updateInfo("channels", json.dumps(self["channels"]))
        return channelMapper

    # 添加社区内组标签
    def createTag(self, tagName:str, channelid:int) -> bool:
        if str(channelid) in dict(self["channels"]).keys() and self["channels"][str(channelid)]["userid"] == self["userid"]:
            channelMapper = Channel(channelid)
            return channelMapper.createTag(tagName)
        return False
    
    # 查询所加入的社区信息
    def queryChannelInfo(self, channelid:int):
        if str(channelid) not in dict(self["channels"]).keys():
            return None
        return Channel(channelid)

    # 加入社区
    def joinChannel(self, channelid:int):
        channelMapper = Channel(channelid)
        if channelMapper.appendMember(self["userid"]):
            self["channels"][str(channelid)] = {"channelid":channelMapper["channelid"], "channelname":channelMapper["channelname"], "userid":channelMapper["userid"]}
            self.updateInfo("channels", json.dumps(self["channels"]))
            return Channel(channelid)
        return None

    # 移除社区某个成员
    def removeChannelMember(self, memberid:int, channelid:int) -> bool:
        if str(channelid) not in dict(self["channels"]).keys():
            return False
        if self["channels"][str(channelid)]["userid"] == self["userid"] and self["userid"] != memberid:
            return User(_userid=memberid).removeChannelMember(memberid, channelid)
        elif memberid == self["userid"] and self["channels"][str(channelid)]["userid"] != memberid:
            channelMapper = Channel(channelid)
            del self["channels"][str(channelid)]
            self.updateInfo("channels", json.dumps(self["channels"]))
            return channelMapper.removeMember(memberid)
        return False

    # 修改个人信息
    def updateInfo(self, key, value) -> bool:
        sql = "UPDATE users SET {}=%s WHERE userid=%s;".format(key)
        self.dbSql.execute(sql, (value, self["userid"]))
        self.initUser(_userid = self["userid"])
        return True
    
    # 添加好友
    def addFriend(self, friendId) -> bool:
        friendMapper = User.queryUserInfoFromId(friendId)
        friendMapper["friends"][str(self["userid"])] = self["username"]
        friendMapper.updateInfo("friends", json.dumps(friendMapper["friends"]))
        self["friends"][str(friendId)] = friendMapper["username"]
        self.updateInfo("friends", json.dumps(self["friends"]))
        return True
    
    # 删除好友
    def delFriend(self, friendId) -> bool:
        try:
            friendMapper = User.queryUserInfoFromId(friendId)
            myselfid = self["userid"]
            if str(myselfid) in friendMapper["friends"].keys():
                del friendMapper["friends"][str(myselfid)]
                friendMapper.updateInfo("friends", json.dumps(friendMapper["friends"]))
            if str(friendId) in self["friends"].keys():
                del self["friends"][str(friendId)]
                self.updateInfo("friends", json.dumps(self["friends"]))
            return True
        except Exception as e:
            print("User.delFriend error:", e)
            return False

    # 插入数据缓存
    def insertCache(self, _data:DataInfo):
        cacheFields = ["chatid", "date", "userid", "type", "sender", "channelid", "tag", "data"]
        insertData = DataInfo()
        for field in cacheFields:
            if field not in _data.keys():
                # print(_data)
                return False
            insertData.setItem(field, _data.get(field))
        chat_cache_table_name = "chat_cache_{}".format(self.get("userid"))
        print(chat_cache_table_name)
        self.dbSql.insertDataEx(chat_cache_table_name, insertData)
        return True
    
    # 检查是不是好友
    def lookFriend(self, userid):
        if str(userid) not in self["friends"].keys():
            return False
        return True

    # 获取缓存信息
    def getCaches(self):
        cache_table_name = "chat_cache_{}".format(self["userid"])
        sql = "SELECT * FROM {};".format(cache_table_name)
        fields, values = self.dbSql.query(sql,None)
        res = []
        for value in values:
            valueInfo = DataInfo()
            for idx, v in enumerate(fields):
                valueInfo[str(v)] =  json.loads(value[idx]) if "data" in v else value[idx]
            res.append(valueInfo)
        return res
    
    # 删除缓存的信息
    def delCache(self, chatid):
        cache_table_name = "chat_cache_{}".format(self["userid"])
        sql = "DELETE FROM {} WHERE chatid=%s;".format(cache_table_name)
        self.dbSql.execute(sql, (chatid,))

    # 插入聊天记录
    def insertChat(self, _data:DataInfo):
        chatFields = ["chatid", "date", "userid", "type", "sender", "data"]
        insertData = DataInfo()
        for field in chatFields:
            if field not in _data.keys():
                return False
            insertData.setItem(field, _data.get(field))
        chat_table_name = "user_chat_{}".format(self.get("userid"))
        self.dbSql.insertDataEx(chat_table_name, insertData)
        return True

    @staticmethod
    def sign(_userInfo:UserInfo):
        userid = int(time.time() * 1000)
        try:
            dbSql = DBMysql()
            _userInfo.setItem("userid", userid)
            fieldsInfo = UserInfo()
            for field in userFields:
                if field in _userInfo.keys():
                    fieldsInfo.setItem(field, _userInfo.get(field))
            fieldsInfo["password"] = User.md5Hash(fieldsInfo["password"])
            dbSql.insertData(fieldsInfo)
            chat_table_name = "user_chat_{}".format(userid)
            chat_table_item = {"chatid":["BIGINT", "NOT NULL"],
                               "date": ["BIGINT", "NOT NULL"],
                               "userid": ["BIGINT", "NOT NULL"],
                               "type": ["INTEGER", "NOT NULL"],
                               "sender": ["BIGINT", "NOT NULL"],
                               "data": ["JSON", "NOT NULL"]
                               }
            dbSql.createTable(chat_table_name, chat_table_item, uniques=["chatid"]) # 聊天记录表（好友）
            
            chat_cache_table_name = "chat_cache_{}".format(userid)
            chat_cache_table_item = {"chatid":["BIGINT", "NOT NULL"],
                                "date": ["BIGINT", "NOT NULL"],
                                "userid": ["BIGINT", "NOT NULL"],
                                "type": ["INTEGER", "NOT NULL"],
                                "sender": ["BIGINT", "NOT NULL"],
                                "channelid": ["BIGINT", "NOT NULL"],
                                "tag": ["VARCHAR(255)", "NOT NULL"],
                                "data": ["JSON", "NOT NULL"]
                               }
            dbSql.createTable(chat_cache_table_name, chat_cache_table_item, uniques=["chatid"]) # 聊天记录缓存表
        except Exception as e:
            print("User.sign Error: {}".format(e))
            return None
        return User(_userid=userid)

    @staticmethod
    def md5Hash(text) -> str:
        """对输入的文本进行MD5哈希"""
        md5_hash = hashlib.md5()
        md5_hash.update(text.encode('utf-8'))
        return md5_hash.hexdigest()
    
    @staticmethod
    def token(data:dict) -> str:
        m = str(data)
        hm = User.md5Hash(m)
        c = pow(int(hm,16),rsa['d'],rsa['N'])
        tok = base64.b64encode(m.encode("utf-8")).decode("utf-8") + "." + hex(c)[2:]
        return tok
    
    @staticmethod
    def checkToken(token:str) -> bool:
        data, sig = token.split(".")
        m = base64.b64decode(data.encode("utf-8")).decode("utf-8")
        hm = User.md5Hash(m)
        r = hex(pow(int(sig,16),rsa['e'],rsa['N']))[2:]
        return int(hm,16) == int(r,16), json.loads(m.replace("'", '"'))
    
    @staticmethod
    def login(email, password):
        password = User.md5Hash(password)
        dbSql = DBMysql()
        sql = "SELECT COUNT(*) FROM users WHERE email=%s AND password=%s;"
        res = dbSql.query(sql, (email, password))
        _, value = res
        if value[0][0] > 0:
            return User(_email=email)
        return None
    
    @staticmethod
    def queryUserInfoFromId(userid):
        dbSql = DBMysql()
        sql = "SELECT COUNT(*) FROM users WHERE userid=%s;"
        res = dbSql.query(sql, (userid, ))
        _, value = res
        if value[0][0] > 0:
            return User(_userid=userid)
        return None
    
    @staticmethod
    def queryUserInfoFromEmail(email):
        dbSql = DBMysql()
        sql = "SELECT COUNT(*) FROM users WHERE email=%s;"
        res = dbSql.query(sql, (email, ))
        _, value = res
        if value[0][0] > 0:
            return User(_email=email)
        return None