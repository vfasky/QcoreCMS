#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date: 2013-09-03 15:25:46
# @Author: vfasky (vfasky@gmail.com)
# @Link: http://vfasky.com
# @Version: $Id$

from xcat.web import RequestHandler, route
from tornado import gen
from tornado.web import asynchronous
from app.models import cms

class RequestHandler(RequestHandler):
    
    # 格式化成json, 并输出
    def jsonify(self, **args):
        data = dict(
            success=args.get('success', True),
            msg=args.get('msg', None),
            data=args.get('data', None),
        )
        self.write(data)
        

@route("/api/category.list")
class CategoryList(RequestHandler):

    @asynchronous
    @gen.engine
    def get(self):
        ar = cms.Category.select()
        data = yield gen.Task(ar.execute)
        print data
        self.finish()
        #self.jsonify(data=data._data)
