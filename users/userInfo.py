from utils.dataInfo import DataInfo
import json

class UserInfo(DataInfo):
    def __init__(self, _info:dict = {}) -> None:
        for key, value in _info.items():
            self.setItem(key, value)
        # self['userid'] = _info['userid']
        # self['username'] = _info['username']
        # self['email'] = _info['email']
        # self['password'] = _info['password']
        # self['headimage'] = _info['headimage']
        # self['birthday'] = _info['birthday']
        # self['gender'] = _info['gender']
        # self['signature'] = _info['signature']
        # self['date'] = _info['date']
        # self['friends'] = json.dumps(_info['friends']) if 'friends' in _info.keys() else json.dumps({})
        # self['channels'] = json.dumps(_info['channels']) if 'channels' in _info.keys() else json.dumps({})
        # self['myself'] = json.dumps(_info['myself']) if 'myself' in _info.keys() else json.dumps({})


    def getTable(self):
        return "users"