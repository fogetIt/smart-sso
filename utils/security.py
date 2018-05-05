# -*- coding: utf-8 -*-
# @Date:   2018-01-02 12:05:08
# @Last Modified time: 2018-01-02 12:05:51
import jwt
from flask import current_app
from passlib.apps import custom_app_context as pwd_context


class Password(object):
    """
    非对称加密
    """
    @staticmethod
    def make(pwd):
        return pwd_context.encrypt(pwd)

    @staticmethod
    def verify(pwd, password):
        return pwd_context.verify(pwd, password)


class Token(object):
    @staticmethod
    def make(payload):
        assert type(payload) is dict
        if payload:
            return jwt.encode(payload, current_app.config.get("SECRET_KEY"), algorithm="HS256")

    @staticmethod
    def verify(jwt_str):
        assert type(jwt_str) is str
        if jwt_str:
            return jwt.decode(jwt_str, current_app.config.get("SECRET_KEY"), algorithms=['HS256'])
