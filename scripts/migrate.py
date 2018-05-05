# -*- coding: utf-8 -*-
# @Date:   2018-02-08 18:00:38
# @Last Modified time: 2018-02-08 18:00:59
from playhouse.migrate import migrate, MySQLMigrator
from models import sso_database


# migrate(
#     MySQLMigrator(sso_database).add_column(
#         'user', 'id', User.id
#     ),
#     MySQLMigrator(sso_database).add_column(
#         'user', 'create_at', User.createAt
#     ),
#     MySQLMigrator(sso_database).add_column(
#         'user', 'modify_at', User.modifyAt
#     ),
#     MySQLMigrator(sso_database).apply_default(
#         'user', 'create_at', User.createAt
#     ),
# )
