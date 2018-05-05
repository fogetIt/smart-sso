# -*- coding: utf-8 -*-
# @Date:   2017-09-19 15:29:36
# @Last Modified time: 2017-09-19 16:23:44
import os
from utils import PY2
from playhouse.pool import PooledMySQLDatabase
if PY2:
    import ConfigParser
else:
    import configparser as ConfigParser


scp = ConfigParser.SafeConfigParser()
conf_file = os.path.join(
    os.path.dirname(__file__), "mysql.ini"
)
scp.read(conf_file)


class __(object): pass


def get_config_string(db_name):
    result = __()
    result.host = scp.get(db_name, "host")
    result.port = scp.getint(db_name, "port")
    result.name = scp.get(db_name, "name")
    result.user = scp.get(db_name, "user")
    result.password = scp.get(db_name, "password")
    result.charset = scp.get(db_name, "charset")
    return result


def create_db_pool(db_name):
    connect_string = get_config_string(db_name)
    db_pool = PooledMySQLDatabase(
        db_name,
        max_connections=20,
        stale_timeout=300,
        timeout=None,
        host=connect_string.host,
        port=connect_string.port,
        user=connect_string.user,
        password=connect_string.password,
    )
    return db_pool


sso_database = create_db_pool("smart_sso")
