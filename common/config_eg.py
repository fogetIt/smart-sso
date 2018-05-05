# -*- coding: utf-8 -*-
# @Date:   2017-11-24 16:42:32
# @Last Modified time: 2018-03-26 12:45:34
from datetime import timedelta
from redis import Redis


class VerificationCodeConfig(object):
    TEST_VERIFICATION_CODE_FAILED = 5        #: 一个帐号验证码验证失败的次数
    SEND_VERIFICATION_CODE_SUCCESS = 10      #: 给一个帐号发送验证码成功的次数
    LAST_VERIFICATION_CODE_EXPIRED = 1 * 60  #: 上一个验证码生效时间（下一个验证码生成间隔时间）
    ACCOUNT_FROZEN_BEFORE = 60 * 60          #: 发送成功或验证错误次数超过限制时，帐号的冻结时间
    MOBILE_REGEX = "^0\d{2,3}\d{7,8}$|^1[358]\d{9}$|^147\d{8}$"     #: 手机号验证规则
    EMAIL_REGEX = "^[^\._-][\w\.-]+@(?:[A-Za-z0-9]+\.)+[A-Za-z]+$"  #: 邮箱验证规则


class FlaskLoginConfig(object):
    REMEMBER_COOKIE_NAME = "sso"
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = timedelta(hours=4)


class FlaskAdminConfig(object):
    SUPER_USER = {"admin": "123zhang"}


class CommonConfig(VerificationCodeConfig, FlaskLoginConfig, FlaskAdminConfig):
    SECRET_KEY = "\xc9&\xca\x12\xe4\xe1\xfd\xe3?\xf4\x80pZ]\x9e/\x9cb|\x17\xc3b\xef\xe3"
    SESSION_TYPE = "redis"
    SESSION_REDIS = Redis(host="localhost")
    SESSION_PERMANENT = False  # remove session when close browser or lifetime timeout
    SESSION_COOKIE_NAME = FlaskLoginConfig.REMEMBER_COOKIE_NAME
    SESSION_COOKIE_HTTPONLY = FlaskLoginConfig.REMEMBER_COOKIE_HTTPONLY
    PERMANENT_SESSION_LIFETIME = FlaskLoginConfig.REMEMBER_COOKIE_DURATION


class Dev(CommonConfig):
    SESSION_COOKIE_SECURE = REMEMBER_COOKIE_SECURE = False


class Pro(CommonConfig):
    SESSION_COOKIE_SECURE = REMEMBER_COOKIE_SECURE = True


class Mail163Config(object):
    MAIL_HOST = "smtp.163.com"
    MAIL_PORT = 25
    MAIL_SSL_PORT = 465
    MAIL_NAME = "xxx"
    MAIL_USER = "xxx@163.com"
    MAIL_PASSWORD = "xxx"
    MAIL_CHARSET = "utf-8"


class MailQQConfig(object):
    MAIL_HOST = "smtp.qq.com"
    MAIL_PORT = 25
    MAIL_SSL_PORT = 465
    MAIL_NAME = "xxx"
    MAIL_USER = "xxx@qq.com"
    MAIL_PASSWORD = "xxx"
    MAIL_CHARSET = "utf-8"


def init_app(app):
    from flask_login import config
    app.config.from_mapping({
        k: v for k, v in filter(lambda t: str.isupper(t[0]), config.__dict__.items())
    })
    CONFIG = Dev if app.config.get("DEBUG") else Pro
    app.config.from_object(CONFIG)
    for i in CONFIG.__bases__:
        app.config.from_object(i)
    if app.config.get("MAIL") == "QQ":
        app.config.from_object(MailQQConfig)
    else:
        app.config.from_object(Mail163Config)
