# -*- coding: utf-8 -*-
# @Date:   2017-11-22 14:15:17
# @Last Modified time: 2017-11-22 14:15:18
import sys
from flask import Flask, current_app
from flask_cors import CORS
from common import (
    config, middlewares, router, super_user,
)
from models import User
from utils import PY2
from patches import SsoSession, SsoLoginManager


if PY2:
    reload(sys)
    sys.setdefaultencoding("utf-8")


app = Flask(__name__)
app.config["MAIL"] = "QQ"
app.config["DEBUG"] = True
login_manager = SsoLoginManager()


config.init_app(app)
CORS().init_app(app)  # Access-Control-Allow-Origin
router.init_app(app)
middlewares.init_app(app)
SsoSession().init_app(app)
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    """
    set user callback
    """
    try:
        _id = int(user_id)
    except:
        _id = 0
    _current_user = User.better_get(User.id == _id)
    if not _current_user:
        if user_id in current_app.config.get("SUPER_USER"):
            return super_user(user_id)
    return _current_user


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=7654)
