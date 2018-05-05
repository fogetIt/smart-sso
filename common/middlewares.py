# -*- coding: utf-8 -*-
# @Date:   2017-11-29 15:37:04
# @Last Modified time: 2017-11-29 15:37:05
from flask import request, abort
from models import sso_database, User, IpWhite


def init_app(app):


    @app.before_first_request
    def create_tables():
        """
        CREATE DATABASE smart_sso CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
        """
        models = User, IpWhite
        for model in models:
            if not model.table_exists():
                model.create_table()


    @app.before_request
    def connect_db():
        """
        如果 mysql 长时间没有新的请求发起，达到超时时间，会自动关闭连接
        """
        if sso_database.is_closed():
            sso_database.connect()


    @app.before_request
    def verify_admin():
        if request.path.startswith("/admin"):
            ip = request.remote_addr
            if ip != "127.0.0.1" and not IpWhite.better_get(IpWhite.ip == ip):
                abort(401)


    app.after_request(lambda response: response)


    @app.teardown_request
    def close_db(exc):
        """
        回收数据库连接，放入连接池
        """
        if not sso_database.is_closed():
            sso_database.close()
