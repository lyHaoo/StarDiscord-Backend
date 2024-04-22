from django.http import HttpRequest
from StarDiscord.stdResponse import StdResponse, StdResponseSucceed, StdResponseFailed
from config.config import noAuthenticationCode
from users.user import User
from utils.captcha import EmailCaptcha

def authentication(f):
    def wrapper(*args, **kwargs):
        request:HttpRequest = args[0]
        if request.method == "POST":
            print(request.bodyJson)
            if "code" not in request.bodyJson.keys() and "token" not in request.bodyJson.keys():
                return StdResponseFailed({"message":"Required field missing."}).jumps()
            if request.bodyJson['code'] in noAuthenticationCode:
                return f(*args, **kwargs)
            res, fileds = User.checkToken(request.bodyJson["token"])
            if not res:
                return StdResponseFailed({"message":"Authentication fails."}).jumps()
            request.bodyJson["userid"] = fileds["userid"]
            request.bodyJson["email"] = fileds["email"]
        elif request.method == "GET":
            print("headers:", request.headers)
            token = request.headers.get("token")
            res, fileds = User.checkToken(token)
            print(res)
            if not res:
                return StdResponseFailed({"message":"Authentication fails."}).jumps()
            request.bodyJson["userid"] = fileds["userid"]
            request.bodyJson["email"] = fileds["email"]
        return f(*args, **kwargs)
    return wrapper

def wsAuthentication(f):
    def wrapper(*args, **kwargs):
        try:
            message:dict = args[1]
            token = message.get("token")
            res, fileds = User.checkToken(token)
            if not res:
                return None
            message["userid"] = fileds["userid"]
            message["email"] = fileds["email"]
            return f(*args, **kwargs)
        except Exception as e:
            return None
    return wrapper

def captchaAuthentication(f):
    def wrapper(*args, **kwargs):
        try:
            request:HttpRequest = args[0]
            email = request.bodyJson["email"]
            captchaCode = request.bodyJson["captcha"]
            print(request.bodyJson)
            res = EmailCaptcha.checkCaptcha(email, captchaCode)
            if not res:
                 return StdResponseFailed({"message":"Verification code error."}).jumps()
            return f(*args, **kwargs)
        except Exception as e:
             return StdResponseFailed({"message":"Verification code error."}).jumps()
    return wrapper