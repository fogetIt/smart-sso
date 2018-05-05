# -*- coding: utf-8 -*-
# @Date:   2018-03-29 13:24:12
# @Last Modified time: 2018-03-29 13:24:20
from flask import jsonify


def json_resp(status=0, msg="", **kwargs):
    _dict = {"status": status, "msg": msg}
    _dict.update(kwargs)
    return jsonify(_dict)
