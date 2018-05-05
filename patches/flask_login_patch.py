# -*- coding: utf-8 -*-
# @Date:   2018-03-26 17:01:34
# @Last Modified time: 2018-03-26 17:01:57
from flask_login import LoginManager


class SsoLoginManager(LoginManager):
    """
    remove set cookie option
    """
    def _set_cookie(self, response): pass
