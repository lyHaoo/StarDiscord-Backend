# from users.userInfo import UserInfo
# from utils.dbMysql import DBMysql
from users.user import User

# if __name__ == "__main__":
#     userinfo = UserInfo({"username":"xxx", "email": "999999@qq.com", "password":"123", "headimage":"/123/123","birthday":123456,"gender":"男","signature":"xjkhasdkj", "date":123465, "friends":{}, "channels":{}, "myself": ["aaa"]})
#     a = DBMysql()
#     print(a.queryData("users", {"userid":99999}))
#     print(a.checkTableExist("users"))
#     print(User.sign(userinfo))

import gmpy2
import hashlib
import json
import base64

def md5Hash(text):
    """对输入的文本进行MD5哈希"""
    md5_hash = hashlib.md5()
    md5_hash.update(text.encode("utf-8"))
    return md5_hash.hexdigest()

p = 3487583947589437589237958723892346254777
q = 8767867843568934765983476584376578389
N = 30578675145816634962204467309994126955968568987449100734690153203822106214253 # p*q
e = 65537
phin = (p - 1) * (q - 1)
d = 19178568796155560423675975774142829153827883709027717723363077606260717434369 # gmpy2.invert(e, phin)
res = {
  "code": 521001,
  "message": "Registered successfully",
  "username": "star",
  "userid": 1712565932373,
  "email": "123456789@qq.com",
  "date": 1712553494539,
  "status": 1
}
# m = str(res)
# m = md5Hash(m)
# c = pow(int(m,16),d,N)
# # 上面是签名

# r = hex(pow(c,e,N))[2:]
# hm = md5Hash(str(res))
# print("r:", r)
# print("hm:", hm)
# print(r == hm)

import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr

##### 配置区  #####
mail_host = 'smtp.qq.com'
mail_port = '465'   #Linux平台上面发
# 发件人邮箱账号
login_sender = '2537632926@qq.com'
# 发件人邮箱授权码而不是邮箱密码，授权码由邮箱官网可设置生成
login_pass = 'aspyslsjkdlsebeh'
#邮箱文本内容
str="test"
#发送者
sendName = "StarDiscord"
#邮箱正文标题
title = "StarDiscord"
########## end  ##########


# 参数是收件人
def sendQQ(receivers):
    msg = MIMEText(str, 'plain', 'utf-8')
    msg['From'] = formataddr([sendName, login_sender])
    # 邮件的标题
    msg['Subject'] = title
    try:
      # 服务器
      server = smtplib.SMTP_SSL(mail_host, mail_port)
      server.login(login_sender, login_pass)
      server.sendmail(login_sender, [receivers, ], msg.as_string())
      print("已发送到" + receivers + "的邮箱中！")
      server.quit()
    except smtplib.SMTPException:
        print("发送邮箱失败！")

if __name__ == '__main__':
    sendQQ('1351574146@qq.com')  #接收人的QQ邮箱