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


@route("/api/category.save", allow=['admin'])
class CategorySave(RequestHandler):

    @asynchronous
    @gen.engine
    @form('app.forms.cms.CategoryAdd')
    def post(self): 
        yield gen.Task(self.form.load_field_data)

        if not self.form.validate():
            self.jsonify(
                success=False,
                msg=' \n '.join(self.format_form_error(self.form)))
            return

        post = self.form.data

        if post['id']:
            category_ar = cms.Category.select()\
                .where(cms.Category.id == post['id'])

            if 0 == (yield gen.Task(category_ar.count)):
                self.jsonify(
                    success=False,
                    msg='not Data')
                return
            category_model = yield gen.Task(category_ar.get)
        else:
            category_model = False

        if post['parent'] != '0':
            #检查上级是否存在
            category_ar = cms.Category.select()\
                .where(cms.Category.id == post['parent'])
            
            if 0 == (yield gen.Task(category_ar.count)):
                self.jsonify(
                    success=False,
                    msg='parent Not Fount')
                return

        if False == category_model:
            # 防止重复添加
            category_ar = cms.Category.select()\
                .where(cms.Category.parent == post['parent'])\
                .where(cms.Category.title == post['title'])\
                .where(cms.Category.desc == post['desc'])\
                .where(cms.Category.table == (yield gen.Task(
                    cms.Table.select().where(cms.Table.id == post['table'])\
                            .get)))

            if 0 != (yield gen.Task(category_ar.count)):
                self.jsonify(
                    success=False,
                    msg='data is has')
                return

            category = cms.Category(**post)
            yield gen.Task(category.save)
        else:
            self.form.data_to_model(category_model)
            yield gen.Task(category_model.save)
                    
        self.jsonify(data=category._data)
        
        



