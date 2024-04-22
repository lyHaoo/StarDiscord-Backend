from django.views.decorators.http import require_GET, require_POST, require_http_methods
from django.http import Http404, HttpRequest, StreamingHttpResponse, HttpResponse
from users.user import UserInfo, User
from StarDiscord.stdResponse import StdResponse, StdResponseSucceed, StdResponseFailed
import os
from StarDiscord.wrappers import authentication, captchaAuthentication
import time
from utils.dataInfo import DataInfo
from users.channel import Channel
from utils.captcha import EmailCaptcha
from utils.dbMysql import DBMysql
import re
import json

def is_valid_email(email):
    # 正则表达式模式用于匹配电子邮件地址的格式
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    # 使用re.match()函数来匹配正则表达式模式
    if re.match(pattern, email):
        return True
    else:
        return False

#图片加载
@require_GET
def loadImage(request:HttpRequest, image_name:str):
    image_path = os.path.join("./StarDiscord/static/images", image_name)
    with open(image_path, 'rb') as f:
        data = f.read()
    return HttpResponse(data, content_type="image/png")

# 注册
@captchaAuthentication
@require_POST
def sign(request:HttpRequest):
    userMustFields = ['code','username', 'email', 'password', 'birthday', 'gender', 'date']
    for tempField in userMustFields:
        if tempField not in request.bodyJson.keys():
            return StdResponseFailed({"message":"Required field missing.", "code":521001, "date":int(time.time()*1000)}).jumps()
    userInfo = UserInfo(request.bodyJson)
    userInfo.setItem("headimage", "std.png")
    userInfo.setItem("signature", "在生命的舞台上，我们扮演着各种角色，有时欢笑，有时泪流，而最美的表演，常是在默默的离场中。")
    userInfo.setItem("friends", {})
    userInfo.setItem("channels", {})
    userInfo.setItem("myself", {})
    sign_res = User.sign(userInfo)
    if sign_res is None:
        return StdResponseFailed({"message":"Fail to register.", "code":521001, "date":int(time.time()*1000)}).jumps()
    
    responseMapper = UserInfo()
    responseMapper.setItem("code", 521001)
    responseMapper.setItem("message", 'Registered successfully')
    responseMapper.setItem("username", sign_res['username'])
    responseMapper.setItem("userid", sign_res['userid'])
    responseMapper.setItem("email", sign_res['email'])
    responseMapper.setItem("date", sign_res['date'])
    return StdResponseSucceed(responseMapper).jumps()


# 修改个人信息
@authentication
@require_GET
def myselfInfo(request:HttpRequest):
    if request.method == "OPTIONS":
        return StdResponseSucceed({"message":"options OK."}).jumps()
    userid = request.bodyJson["userid"]
    userMapper = User(_userid=userid)
    responseMapper = DataInfo()
    responseMapper.setItem("code",531009)
    responseMapper.setItem("status",1)
    responseMapper.setItem("date",int(time.time()*1000))
    responseMapper.setItem("userid",userMapper["userid"])
    responseMapper.setItem("username",userMapper["username"])
    responseMapper.setItem("email",userMapper["email"])
    responseMapper.setItem("headimage",userMapper["headimage"])
    responseMapper.setItem("birthday",userMapper["birthday"])
    responseMapper.setItem("gender",userMapper["gender"])
    responseMapper.setItem("signature",userMapper["signature"])
    responseMapper.setItem("friends",userMapper["friends"])
    responseMapper.setItem("channels",userMapper["channels"])
    responseMapper.setItem("myself",userMapper["myself"])
    return StdResponseSucceed(responseMapper).jumps()

# 创建频道
@authentication
@require_POST
def newChannels(request:HttpRequest):
    userMapper = User(_userid = request.bodyJson["userid"])
    res = userMapper.newChannel(request.bodyJson["channelname"])
    if res is None:
        return StdResponseFailed({"message":"Channel creation failure.", "code":531003, "date":int(time.time()*1000)}).jumps()
    responseMapper = DataInfo()
    responseMapper.setItem("code", 531003)
    responseMapper.setItem("message", 'Channel creation successfully')
    responseMapper.setItem("date", int(time.time()*1000))
    responseMapper.setItem("channelid", res["channelid"])
    responseMapper.setItem("channelname", res["channelname"])
    responseMapper.setItem("owner", res["userid"])
    responseMapper.setItem("admin", res["admin"])
    responseMapper.setItem("member", res["member"])
    responseMapper.setItem("tags", res["tags"])
    return StdResponseSucceed(responseMapper).jumps()

# 加入频道
@authentication
@require_POST
def joinChannel(request:HttpRequest):
    userMapper = User(_userid = request.bodyJson["userid"])
    res = userMapper.joinChannel(request.bodyJson["channelid"])
    if res is None:
        return StdResponseFailed({"message":"Community membership failure.", "code":531004, "date":int(time.time()*1000)}).jumps()
    responseMapper = DataInfo()
    responseMapper.setItem("code", 531004)
    responseMapper.setItem("message", 'Channel joining success.')
    responseMapper.setItem("date", int(time.time()*1000))
    responseMapper.setItem("channelid", res["channelid"])
    responseMapper.setItem("channelname", res["channelname"])
    responseMapper.setItem("owner", res["userid"])
    responseMapper.setItem("admin", res["admin"])
    responseMapper.setItem("member", res["member"])
    responseMapper.setItem("tags", res["tags"])
    return StdResponseSucceed(responseMapper).jumps()

# 退出频道
@authentication
@require_POST
def quitChannel(request:HttpRequest):
    userMapper = User(_userid = request.bodyJson["userid"])
    res = userMapper.removeChannelMember(request.bodyJson["operated"], request.bodyJson["channelid"])
    if not res:
        return StdResponseFailed({"message":"Channel exit failure.", "code":531005, "date":int(time.time()*1000)}).jumps()
    return StdResponseSucceed({"message":"Channel exit success.", "code":531005, "date":int(time.time()*1000)}).jumps()

# 获取频道信息
@authentication
@require_GET
def channelInfo(request:HttpRequest):
    userMapper = User(_userid = request.bodyJson["userid"])
    channelid = request.GET.get("channelid")
    try:
        channelid = int(channelid)
    except Exception as e:
        return StdResponseFailed({"message":"Failed to obtain channel information.", "code":531006, "date":int(time.time()*1000)}).jumps()
    res = userMapper.queryChannelInfo(channelid)
    if res is None:
        return StdResponseFailed({"message":"Failed to obtain channel information.", "code":531006, "date":int(time.time()*1000)}).jumps()
    responseMapper = DataInfo()
    responseMapper.setItem("code", 531006)
    responseMapper.setItem("message", 'Obtaining channel information succeeded. ')
    responseMapper.setItem("date", int(time.time()*1000))
    responseMapper.setItem("channelid", res["channelid"])
    responseMapper.setItem("channelname", res["channelname"])
    responseMapper.setItem("owner", res["userid"])
    responseMapper.setItem("admin", res["admin"])
    responseMapper.setItem("member", res["member"])
    responseMapper.setItem("tags", res["tags"])
    return StdResponseSucceed(responseMapper).jumps()


# 添加好友
@authentication
@require_POST
def addFriend(request:HttpRequest):
    userid = request.bodyJson["userid"]
    friendid = request.bodyJson["friendid"]
    userMapper = User(_userid=userid)
    ret = userMapper.addFriend(friendid)
    if not ret:
        return StdResponseFailed({"message":"Add friend failed.", "code":531001, "date":int(time.time()*1000)}).jumps()
    return StdResponseSucceed({"message":"Add friend succeeded.", "code":531001, "date":int(time.time()*1000)}).jumps()

# 删除好友
@authentication
@require_POST
def delFriend(request:HttpRequest):
    userid = request.bodyJson["userid"]
    friendid = request.bodyJson["friendid"]
    userMapper = User(_userid=userid)
    ret = userMapper.delFriend(friendid)
    if not ret:
        return StdResponseFailed({"message":"Del friend failed.", "code":531002, "date":int(time.time()*1000)}).jumps()
    return StdResponseSucceed({"message":"Del friend succeeded.", "code":531002, "date":int(time.time()*1000)}).jumps()

# 查找好友是否存在
@authentication
@require_GET
def queryUser(request:HttpRequest):
    userid = request.GET.get("id")
    try:
        userid = int(userid)
    except Exception as e:
        return StdResponseFailed({"message":"Failed to find a friend. The request parameters are incorrect.", "code":531010, "date":int(time.time()*1000)}).jumps()
    userInfo = User.queryUserInfoFromId(userid)
    if userInfo is None:
        return StdResponseFailed({"message":"Failed to find a friend.", "code":531010, "date":int(time.time()*1000)}).jumps()
    responseMapper = DataInfo()
    responseMapper.setItem("code", 531010)
    responseMapper.setItem("status", 1)
    responseMapper.setItem("date", int(time.time()*1000))
    responseMapper.setItem("userid", userInfo.get("userid"))
    responseMapper.setItem("username", userInfo.get("username"))
    responseMapper.setItem("gender", userInfo.get("gender"))
    responseMapper.setItem("birthday", userInfo.get("birthday"))
    responseMapper.setItem("signature", userInfo.get("signature"))
    return StdResponseSucceed(responseMapper).jumps()


# 修改用户密码
@captchaAuthentication
@require_POST
def changePasswd(request:HttpRequest):
    email = request.bodyJson["email"]
    password = request.bodyJson["password"]
    if email == "" or password == "":
        return StdResponseFailed({"message":"Failed to change the password.", "code":531007, "date":int(time.time()*1000)}).jumps()
    userInfo = User.queryUserInfoFromEmail(email)
    if userInfo is None:
        return StdResponseFailed({"message":"Failed to change the password.", "code":531007, "date":int(time.time()*1000)}).jumps()
    ret = userInfo.updateInfo("password", User.md5Hash(password))
    if not ret:
        return StdResponseFailed({"message":"Failed to change the password.", "code":531007, "date":int(time.time()*1000)}).jumps()
    return StdResponseSucceed({"message":"Password changed successfully.", "code":531007, "date":int(time.time()*1000)}).jumps()


# 查找好友是否存在
@authentication
@require_GET
def queryChannelInfo(request:HttpRequest):
    channelid = request.GET.get("channelid")
    try:
        channelid = int(channelid)
    except Exception as e:
        return StdResponseFailed({"message":"Failed to find a channel. The request parameters are incorrect.", "code":531011, "date":int(time.time()*1000)}).jumps()
    chaneelInfo = Channel.queryChannel(channelid)
    if chaneelInfo is None:
        return StdResponseFailed({"message":"Failed to find a channel.", "code":531011, "date":int(time.time()*1000)}).jumps()
    responseMapper = DataInfo()
    responseMapper.setItem("code", 531011)
    responseMapper.setItem("status", 1)
    responseMapper.setItem("date", int(time.time()*1000))
    responseMapper.setItem("channelid", chaneelInfo.get("channelid"))
    responseMapper.setItem("channelname", chaneelInfo.get("channelname"))
    return StdResponseSucceed(responseMapper).jumps()

# 获取验证码
@require_GET
def getCaptcha(request:HttpRequest):
    email = request.headers.get("email")
    if email is None or not is_valid_email(email):
        return StdResponseFailed({"message":"Wrong email address.", "code":531012, "date":int(time.time()*1000)}).jumps()
    code = EmailCaptcha.sendCaptcha(email)
    if code is None:
        return StdResponseFailed({"message":"Failed to send the verification code.", "code":531012, "date":int(time.time()*1000)}).jumps()
    return StdResponseSucceed({"code":531012, "date":int(time.time()*1000), "message":"The verification code is sent successfully. "}).jumps()

# 获取聊天记录
@authentication
@require_GET
def pullChats(request:HttpRequest):
    id = request.GET.get("id")
    page = request.GET.get("page")
    pageSize = request.GET.get("pagesize")
    if id is None or page is None or pageSize is None:
        return StdResponseFailed({"message":"Request parameter error.", "code":551001, "date":int(time.time()*1000)}).jumps()
    try:
        id = int(id)
        page = int(page)
        pageSize = int(pageSize)
    except Exception as e:
        return StdResponseFailed({"message":"Request parameter error.", "code":551001, "date":int(time.time()*1000)}).jumps()
    if pageSize > 100:
        pageSize = 100
    if page <= 0:
        page = 1
    offset = (page - 1) * pageSize
    dbSql = DBMysql()
    fields = []
    values = []
    if len(str(id)) == 13:
        chat_table_name = "user_chat_{}".format(id)
        sql = "SELECT * FROM {} WHERE userid=%s OR sender=%s LIMIT %s OFFSET %s;".format(chat_table_name)
        fields, values = dbSql.query(sql, [id, id, pageSize, offset])
    elif len(str(id)) == 15:
        tag = request.headers.get("tag")
        if tag is None:
            return StdResponseFailed({"message":"Request parameter error.", "code":551001, "date":int(time.time()*1000)}).jumps()
        chat_table_name = "channel_chat_{}".format(id)
        sql = "SELECT * FROM {} WHERE channelid=%s AND tag=%s LIMIT %s OFFSET %s;".format(chat_table_name)
        fields, values = dbSql.query(sql, [id, tag, pageSize, offset])
    else:
        return StdResponseFailed({"message":"Request parameter error.", "code":551001, "date":int(time.time()*1000)}).jumps()
    res = []
    for value in values:
        valueInfo = DataInfo()
        for index, key in enumerate(fields):
            v = value[index]
            if key == "data":
                v = json.loads(v)
            valueInfo.setItem(key, v)
        res.append(valueInfo)
    responseMapper = DataInfo()
    responseMapper.setItem("code", 551001)
    responseMapper.setItem("date", int(time.time()*1000))
    responseMapper.setItem("id", id)
    responseMapper.setItem("data", res)
    return StdResponseSucceed(responseMapper).jumps()


# 添加新的标签
@authentication
@require_POST
def addTag(request:HttpRequest):
    channelid = request.bodyJson["channelid"]
    userid = request.bodyJson["userid"]
    tag = request.bodyJson["tag"]
    channelMapper = Channel(channelid)
    if int(userid) != channelMapper["userid"]:
        return StdResponseFailed({"message":"Insufficient permission, illegal operation.", "code":531013, "date":int(time.time()*1000)}).jumps()
    if not channelMapper.addTag(tag):
        return StdResponseFailed({"message":"Failed to add tag.", "code":531013, "date":int(time.time()*1000)}).jumps()
    channelMapper = Channel(channelid)
    responseMapper = DataInfo()
    responseMapper.setItem("code", 531013)
    responseMapper.setItem("date", int(time.time()*1000))
    responseMapper.setItem("channelid", channelMapper["channelid"])
    responseMapper.setItem("channelname", channelMapper["channelname"])
    responseMapper.setItem("userid", channelMapper["userid"])
    responseMapper.setItem("admin", channelMapper["admin"])
    responseMapper.setItem("member", channelMapper["member"])
    responseMapper.setItem("tags", channelMapper["tags"])
    responseMapper.setItem("counter", channelMapper["counter"])
    return StdResponseSucceed(responseMapper).jumps()