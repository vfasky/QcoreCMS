#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2013-08-24 16:23:58
# @Author  : vfasky (vfasky@gmail.com)
# @Link    : http://vfasky.com
# @Version : $Id$
from xcat.utils import sha1
from xcat.web import RequestHandler, route 
from tornado import gen
from tornado.web import asynchronous
from app import models
from app.models import cms

import time

@route(r"/")
class Index(RequestHandler):
    """Home"""

    def get(self):
        self.write('hello QcoreCMS')

@route(r"/install")
class Install(RequestHandler):
    """Install"""

    @gen.engine
    def creat_tables(self, keys, class_list, callback):
        for v in keys:
            if hasattr(class_list, v):
                model = getattr(class_list, v)
                exists = yield gen.Task(model.table_exists) 
                if exists:
                    # self.write('install error: table exists')
                    # self.finish()
                    # callback(False)
                    # return
                    pass
                else:
                    yield gen.Task(model.create_table) 

        callback(True)

    @asynchronous
    @gen.engine
    def get(self):
        base = ('User', 'Role', 'UserRole')
        cms_base = ('Table', 'FieldUi','Category')

        ret = yield gen.Task(self.creat_tables, base, models)
        if ret:
            ret = yield gen.Task(self.creat_tables, cms_base, cms) 
        else:
            return

        if ret:
            # 创建角色
            role_count = yield gen.Task(
                models.Role.select().count
            )
            if 0 == role_count:
                # 初始化角色
                admin_role = models.Role()
                admin_role.code = 'admin'
                admin_role.name = '管理员'
                yield gen.Task(admin_role.save)

                user_role = models.Role()
                user_role.code = 'user'
                user_role.name = '会员'
                yield gen.Task(user_role.save)

                # 创建管理员 
                settings = self.settings

                user = models.User()
                user.name = settings['admin_name']
                user.email = settings['admin_email']
                user.password = sha1(settings['admin_passwd'])
                user.register_date = time.time()
                yield gen.Task(user.save) 

                user_role = models.UserRole()
                user_role.user = user
                user_role.role = admin_role
                yield gen.Task(user_role.save)

            self.write('ok')
            self.finish()

          