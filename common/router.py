# -*- coding: utf-8 -*-
# @Date:   2018-02-01 13:42:35
# @Last Modified time: 2018-02-01 13:42:52
from controller import sso, registered_admin


def init_app(app):
    registered_admin(app, url_prefix="/admin")
    app.register_blueprint(sso, url_prefix="/api/v1")
