import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
import random
import threading
import time

##### 配置区  #####
mail_host = 'smtp.qq.com'
mail_port = '465'   #Linux平台上面发
# 发件人邮箱账号
login_sender = '2537632926@qq.com'
# 发件人邮箱授权码而不是邮箱密码，授权码由邮箱官网可设置生成
login_pass = 'aspyslsjkdlsebeh'
#发送者
sendName = "StarDiscord"
#邮箱正文标题
title = "StarDiscord个人隐私验证"
########## end  ##########

class EmailCaptcha():
    captchas = {}
    _captchaLock = threading.Lock()
    def __init__(self) -> None:
        pass

    @staticmethod
    def sendCaptcha(email):
        code = random.randint(100000,999999)
        msg = MIMEText("StarDiscord个人隐私验证码：{} 有效期：2分钟。".format(code), 'plain', 'utf-8')
        msg['From'] = formataddr([sendName, login_sender])
        # 邮件的标题
        msg['Subject'] = title
        try:
            # 服务器
            server = smtplib.SMTP_SSL(mail_host, mail_port)
            server.login(login_sender, login_pass)
            server.sendmail(login_sender, [email, ], msg.as_string())
            print("已发送到" + email + " " + str(code) + "的邮箱中！")
            server.quit()
            EmailCaptcha.updateCaptcha(email, code)
            return code
        except Exception as e:
            return None
    
    @staticmethod
    def updateCaptcha(_email,_code):
        with EmailCaptcha._captchaLock:
            EmailCaptcha.captchas[str(_email)] = {"code":_code, "timestamp":time.time()}
    
    @staticmethod
    def checkCaptcha(_email, _code):
        timestamp = time.time()
        with EmailCaptcha._captchaLock:
            for key, value in EmailCaptcha.captchas.items():
                if timestamp - value["timestamp"] > 120:
                    del EmailCaptcha.captchas[key]
        
            if _email in EmailCaptcha.captchas.keys() and int(EmailCaptcha.captchas[_email]["code"]) == int(_code):
                del EmailCaptcha.captchas[_email]
                return True
        return False