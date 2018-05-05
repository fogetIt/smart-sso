# -*- coding: utf-8 -*-
# @Date:   2018-03-29 13:19:55
# @Last Modified time: 2018-03-29 13:20:01
import datetime
from peewee import (Model, CharField)
from playhouse.shortcuts import model_to_dict
from utils import Password


class PasswordField(CharField):

    def db_value(self, value):
        """
        Convert the python value for storage in the database.
        """
        value = Password.make(value) if value else value
        return super(PasswordField, self).db_value(value)


class SsoModel(Model):

    @classmethod
    def update(cls, __data=None, **update):
        update.update({"modifyAt": datetime.datetime.now()})
        return super(SsoModel, cls).update(__data, **update)

    @classmethod
    def get_dict(cls, *expressions):
        _ = cls.better_get(*expressions)
        if _:
            return model_to_dict(_)
        return None

    @classmethod
    def better_get(cls, *query, **kwargs):
        sq = super(SsoModel, cls).select()
        if query:
            sq = sq.where(*query)
        if kwargs:
            sq = sq.filter(**kwargs)
        return sq[0] if sq else None
