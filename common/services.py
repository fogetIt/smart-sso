# -*- coding: utf-8 -*-
# @Date:   2017-11-24 14:14:15
# @Last Modified time: 2017-11-24 14:15:04
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
from email.mime.multipart import MIMEMultipart
from flask import current_app
from flask_login import UserMixin


class Mail(object):

    @classmethod
    def create_message(cls, to_list, subject, content, content_type="plain"):
        """
        构建邮件内容、标题、发件人昵称、收件人昵称
        """
        config = current_app.config
        message = MIMEText(content, _subtype=content_type, _charset=config.get("MAIL_CHARSET"))
        message["Subject"] = subject
        message["From"] = formataddr(
            (config.get("MAIL_NAME"), config.get("MAIL_USER")), charset=config.get("MAIL_CHARSET")
        )
        message["To"] = ";".join(to_list)
        return message.as_string()

    @classmethod
    def create_multi_part_message(cls, to_list, subject, content, content_type="plain"):
        message = MIMEMultipart()
        text = cls.create_message(content, subject, to_list, content_type=content_type)
        message.attach(text)
        return message

    @classmethod
    def send_email(cls, to_list=None, subject=None, content=None, content_type=None, ssl=True):
        server = cls.create_server(ssl=ssl)
        if not server:
            return False
        try:
            message = cls.create_message(to_list, subject, content, content_type=content_type)
            server.sendmail(current_app.config.get("MAIL_USER"), to_list, message)
            server.quit()
            return True
        except Exception as e:
            print("send email error:", e)
            return False

    @classmethod
    def create_server(cls, ssl=True):
        config = current_app.config
        try:
            server = smtplib.SMTP_SSL(
                host=config.get("MAIL_HOST"), port=config.get("MAIL_SSL_PORT")
            ) if ssl else smtplib.SMTP(
                host=config.get("MAIL_HOST"), port=config.get("MAIL_PORT")
            )
            server.login(config.get("MAIL_USER"), config.get("MAIL_PASSWORD"))
            return server
        except Exception as e:
            print("smtp server error:", e)
            return None

    @classmethod
    def send_verification_code(cls, to_list=None, code=None):
        subject = "smart-sso 验证码"
        content = "<p>您的验证码是：<span style='color:red'>%s</span>，请在1分钟内完成操作。</p>" % code
        return cls.send_email(to_list=to_list, subject=subject, content=content, content_type="html")


def send_mobile(code):
    return True


super_user = lambda user_id: type(
    "super_user",
    (UserMixin,),
    {"id": user_id, "password":current_app.config.get("SUPER_USER").get(user_id)}
)()
