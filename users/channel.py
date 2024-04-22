from utils.dataInfo import DataInfo
import time
from utils.dbMysql import DBMysql
import json
from users.cacheUser import insertCacheUser

class ChannelInfo(DataInfo):
    def __init__(self) -> None:
        pass

    def getTable(self):
        return "channels"


class Channel(ChannelInfo):
    def __init__(self, channelid:int) -> None:
        self.dbSql = DBMysql()
        self.initInfo(channelid)

    def initInfo(self, channelid:int):
        jsonFields = ["admin", "member", "tags"]
        if channelid is not None:
            fields, values = self.dbSql.queryData("channels", {"channelid":channelid})

        if fields is not None and values is not None and len(values) > 0:
            values = values[0]
            for index, value in enumerate(values):
                self[fields[index]] = json.loads(value) if fields[index] in jsonFields else value

    # 添加标签
    def createTag(self, tageName):
        # 检测当前标签是否存在
        _, res = self.dbSql.queryData("channels", {"channelid":self["channelid"]})
        res = res[0]
        tags = list(json.loads(res[7]))
        for name in tags:
            if name == tageName:
                return False
        counter = res[8]
        # 添加新的标签
        counter += 1
        tags.append(tageName)
        sql = "UPDATE channels SET tags=%s, counter=%s WHERE channelid=%s;"
        self.dbSql.execute(sql, [json.dumps(tags), counter, self["channelid"]])
        self.initInfo(int(self["channelid"]))
        return True
    
    # 添加成员
    def appendMember(self, memberid:int) -> bool:
        try:
            _, res = self.dbSql.queryData("channels", {"channelid":self["channelid"]})
            res = res[0]
            members = list(json.loads(res[6]))
            if memberid in members:
                return True
            members.append(memberid)
            sql = "UPDATE channels SET member=%s WHERE channelid=%s;"
            self.dbSql.execute(sql, [json.dumps(members), self["channelid"]])
            self.initInfo(int(self["channelid"]))
            return True
        except Exception as e:
            print("Channel.appendMember error:", e)
            return False
    
    # 移除成员
    def removeMember(self, memberid:int) -> bool:
        try:
            _, res = self.dbSql.queryData("channels", {"channelid":self["channelid"]})
            res = res[0]
            members = list(json.loads(res[6]))
            if memberid in members:
                members.remove(memberid)
                sql = "UPDATE channels SET member=%s WHERE channelid=%s;"
                self.dbSql.execute(sql, [json.dumps(members), self["channelid"]])
                self.initInfo(int(self["channelid"]))
            return True
        except Exception as e:
            print("Channel.removeMember error:", e)
            return False
    
    # 插入聊天记录
    def insertChat(self, _data:DataInfo):
        chatid = int(time.time() * 1000)
        _data["chatid"] = chatid
        chatInfo = DataInfo()
        chatInfo.setItem("chatid", chatid)
        chatInfo.setItem("sender", _data["userid"])
        chatInfo.setItem("date", chatid)
        chatInfo.setItem("channelid", self["channelid"])
        chatInfo.setItem("tag", _data["data"]["tag"])
        chatInfo.setItem("data", _data["data"])
        channel_chat_table_name = "channel_chat_{}".format(self.get("channelid"))
        self.dbSql.insertDataEx(channel_chat_table_name, chatInfo)
        self.insertCache(_data)

    # 将待发送消息插入到所有用户的缓存中
    def insertCache(self, _data:DataInfo):
        members = [int(userid) for userid in self["member"]]
        cacheMapper = DataInfo()
        cacheMapper.setItem("chatid",_data["chatid"])
        cacheMapper.setItem("date",_data["chatid"])
        cacheMapper.setItem("type",2)
        cacheMapper.setItem("sender",_data["userid"])
        cacheMapper.setItem("channelid", self["channelid"])
        cacheMapper.setItem("tag", _data["data"]["tag"])
        cacheMapper.setItem("data", _data["data"])
        for recvid in members:
            if recvid == int(_data["userid"]):
                continue
            try:
                cacheMapper.setItem("userid", recvid)
                insertCacheUser(recvid, cacheMapper)
            except Exception as e:
                print("Channel.insertCache error:",e)

    # 添加新的tag
    def addTag(self, tag) -> bool:
        try:
            if tag in self["tags"]:
                return True
            self["tags"] = list(self["tags"])
            self["tags"].append(tag)
            self["counter"] = int(self["counter"]) + 1
            self.updateInfo("tags", json.dumps(self["tags"]))
            self.updateInfo("counter", self["counter"])
            return True
        except Exception as e:
            print("channelInfo.addTag error:", e)
            return False

    # 更新数据
    def updateInfo(self, key, value):
        sql = "UPDATE channels SET {}=%s WHERE channelid=%s;".format(key)
        self.dbSql.execute(sql, (value, self["channelid"]))
        self.initInfo(self["channelid"])
        return True

    # 创建频道社区
    @staticmethod
    def create(channelName:str, userid:int):
        channelid = int(time.time() * 100000)
        try:
            dbSql = DBMysql()
            channelFields = ChannelInfo()
            channelFields.setItem("channelid", channelid)
            channelFields.setItem("channelname", channelName)
            channelFields.setItem("date", channelid)
            channelFields.setItem("userid", userid)
            channelFields.setItem("admin", [userid])
            channelFields.setItem("member", [userid])
            channelFields.setItem("tags", ["chat"])
            channelFields.setItem("counter", 1)
            dbSql.insertData(channelFields)

            channel_chat_table_name = "channel_chat_{}".format(channelid)
            channel_chat_table_item = {"chatid":["BIGINT", "NOT NULL"],
                                        "sender": ["BIGINT", "NOT NULL"],
                                        "date": ["BIGINT", "NOT NULL"],
                                        "channelid": ["BIGINT", "NOT NULL"],
                                        "tag": ["VARCHAR(255)", "NOT NULL"],
                                        "data": ["JSON", "NOT NULL"]
                                        }
            dbSql.createTable(channel_chat_table_name, channel_chat_table_item, uniques=["chatid"])
        except Exception as e:
            print("Channel.create Error: {}".format(e))
            return None
        return Channel(channelid=channelid)
    
    # 频道查询
    @staticmethod
    def queryChannel(channelid):
        dbSql = DBMysql()
        sql = "SELECT COUNT(*) FROM channels WHERE channelid=%s;"
        res = dbSql.query(sql, (channelid, ))
        _, value = res
        if value[0][0] > 0:
            return Channel(channelid)
        return None