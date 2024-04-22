from utils.dataInfo import DataInfo

def insertCacheUser(userid,data:DataInfo):
    from users.user import User
    userMapper = User(_userid=userid)
    return userMapper.insertCache(data)