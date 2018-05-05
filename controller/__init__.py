# -*- coding: utf-8 -*-
# @Date:   2018-01-02 10:59:44
# @Last Modified time: 2018-01-02 14:33:58
"""
Use flask.Blueprint to build pluggable modules.
"""
from flask import Blueprint
from flask_restful import Api
from flask_admin import Admin
from .sso import User, VerificationCode, Session
from redis import Redis
from .admin import IpWhiteView, UserView, AdminIndexView, RedisCliView
from models import IpWhite, User as U


sso = Blueprint("sso", __name__)
# sso.before_request(...)
api = Api(sso)
api.add_resource(User, "/user")
api.add_resource(Session, "/session")
api.add_resource(VerificationCode, "/verification/code")


def registered_admin(app, url_prefix="/admin"):
    admin = Admin()
    admin.init_app(
        app, index_view=AdminIndexView(
            name=u'后台管理系统', url=url_prefix, template="admin.html"
        )
    )
    admin.add_view(IpWhiteView(IpWhite, name=u"ip白名单"))
    admin.add_view(UserView(U, name=u"用户"))
    admin.add_view(RedisCliView(Redis(), name=u"redis控制台"))
