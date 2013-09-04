#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date: 2013-09-03 15:25:46
# @Author: vfasky (vfasky@gmail.com)
# @Link: http://vfasky.com
# @Version: $Id$

from xcat.web import RequestHandler, route, form
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
        if not self._finished:
            self.finish()
           
    # 格式化表单错误信息
    def format_form_error(self, form):
        msg = []
        for v in form:
            for e in v.errors:
                msg.append('%s : %s' % (v.name, e))

        return msg


@route("/api/category.list")
class CategoryList(RequestHandler):

    @asynchronous
    @gen.engine
    def get(self):
        tree = yield gen.Task(cms.Category.td_tree)
        self.jsonify(data=tree)


@route("/api/category.add")
class CategoryAdd(RequestHandler):

    @asynchronous
    @gen.engine
    @form('app.forms.cms.CategoryAdd')
    def get(self): #todo change post
        yield gen.Task(self.form.load_field_data)

        if not self.form.validate():
            self.jsonify(
                success=False,
                msg=' \n '.join(self.format_form_error(self.form))
            )
            return

        post = self.form.data

        if post.parent == '0':
            # 一级分类
            pass
        



