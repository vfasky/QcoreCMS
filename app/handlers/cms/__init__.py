#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2013-08-24 16:23:58
# @Author  : vfasky (vfasky@gmail.com)
# @Link    : http://vfasky.com
# @Version : $Id$

from xcat.web import RequestHandler, route 
from tornado import gen
from tornado.web import asynchronous
from app import models
from app.models import cms

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
            self.write('ok')
            self.finish()

          