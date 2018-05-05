# -*- coding: utf-8 -*-
# @Date:   2017-10-13 14:37:53
# @Last Modified time: 2017-10-13 14:37:54
import datetime
from peewee import (
    PrimaryKeyField, CharField, DateTimeField, DecimalField, IntegerField
)
from flask_login import UserMixin
from patches import PasswordField, SsoModel
from .source import sso_database


class BsModel(SsoModel):

    class Meta:
        database = sso_database


class User(BsModel, UserMixin):
    id = PrimaryKeyField(
        verbose_name="ID", unique=True
    )
    mobile = DecimalField(
        verbose_name="电话", max_digits=11, default=0, decimal_places=0
    )
    email = CharField(
        verbose_name="邮箱", max_length=50, default=""
    )
    password = PasswordField(
        verbose_name="密码", max_length=120, null=True
    )
    status = IntegerField(
        verbose_name="状态", choices=[0, 1], default=0, help_text="0：未激活，1：激活"
    )
    createAt = DateTimeField(
        verbose_name="创建时间", db_column="create_at", null=True
    )
    modifyAt = DateTimeField(
        verbose_name="修改时间", db_column="modify_at", default=datetime.datetime.now
    )
    createIp = CharField(
        verbose_name="创建IP", max_length=20, db_column="create_ip", default=""
    )
    lastLoginAt = DateTimeField(
        verbose_name="最后登录时间", db_column="last_login_at", null=True
    )
    lastLoginIp = CharField(
        verbose_name="最后登录IP", db_column="last_login_ip", max_length=20, default=""
    )

    @classmethod
    def get_dict(cls, *expressions):
        _dict = super(User, cls).get_dict(*expressions)
        _dict.pop("password")
        _dict.update({
            "mobile": int(_dict.get("mobile")),
            "createAt": _dict.get("createAt").timestamp(),
            "modifyAt": _dict.get("modifyAt").timestamp(),
            "lastLoginAt": _dict.get("lastLoginAt").timestamp(),
        })
        return _dict

    class Meta:
        db_table = "user"
        indexes = (
            (("mobile", "email"), True),
        )


class IpWhite(BsModel):
    id = PrimaryKeyField(
        unique=True
    )
    ip = CharField(
        verbose_name="IP", max_length=20, unique=True
    )
    description = CharField(
        verbose_name="描述", max_length=20
    )
    creator = CharField(
        verbose_name="创建者", max_length=20, db_column="creator", unique=True
    )
    createAt = DateTimeField(
        verbose_name="创建时间", db_column="create_at", default=datetime.datetime.now
    )
    modifyAt = DateTimeField(
        verbose_name="修改时间", db_column="modify_at", null=True
    )

    class Meta:
        db_table = "ip_white"
