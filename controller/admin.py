# -*- coding: utf-8 -*-
# @Date:   2017-11-22 15:10:16
# @Last Modified time: 2017-11-22 15:12:23
from flask import request, current_app
from flask_admin import BaseView, expose
from flask_admin.contrib.peewee import ModelView
from flask_login import current_user, login_user, UserMixin
from flask_admin.contrib import rediscli
from models import User
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired
from utils import Password
from common import super_user


class AdminLoginForm(FlaskForm):
    id = StringField(label=u"ID", validators=[DataRequired()])
    password = StringField(label=u"密码", validators=[DataRequired()])


class AuthModelView(ModelView):

    def is_accessible(self):
        return current_user.is_authenticated


class AdminIndexView(BaseView):

    def __init__(self, name=None, category=None, endpoint=None, url=None, template=None):
        super(AdminIndexView, self).__init__(
            name, category, endpoint or 'admin', url or '/admin', 'static'
        )
        self._template = template

    @expose(url='/', methods=('GET', 'POST'))
    def index(self):
        id = request.form.get("id")
        password = request.form.get("password")
        try:
            _id = int(id)
        except:
            _id = 0

        if request.method == "POST":

            _current_user = User.better_get(User.id == _id)
            if _current_user and Password.verify(password, _current_user.password):
                login_user(_current_user, remember=True)
            elif current_app.config.get("SUPER_USER").get(id) == password:
                _super_user = super_user(id)
                login_user(_super_user, remember=True)

        if current_user.is_anonymous:
            id = ""
        else:
            id = current_user.id
        return self.render(self._template, form=AdminLoginForm(), id=id)

class UserView(AuthModelView):
    can_delete = False
    can_edit = False
    can_create = False
    column_labels = dict(
        createAt=u'创建时间',
        modifyAt=u'修改时间',
        email=u'邮箱',
        mobile=u'手机号',
        status=u'用户状态',
        createIp=u'创建IP',
        lastLoginAt=u'最后登录时间',
        lastLoginIp=u'最后登录IP',
    )
    column_exclude_list = ['password']


class IpWhiteView(AuthModelView):
    column_labels = dict(
        ip=u"IP",
        creator=u'创建者',
        createAt=u'创建时间',
        modifyAt=u'修改时间',
        description=u"使用说明（使用单位）"
    )


class RedisCliView(rediscli.RedisCli):

    def is_accessible(self):
        return current_user.is_authenticated
