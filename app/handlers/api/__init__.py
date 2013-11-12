#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date: 2013-09-03 15:25:46
# @Author: vfasky (vfasky@gmail.com)
# @Link: http://vfasky.com
# @Version: $Id$

from xcat.web import RequestHandler, route, form, validator
from tornado import gen
from tornado.web import asynchronous 
from app.models import cms
from tornado.util import import_object

from .helpers import admin_menu

class RequestHandler(RequestHandler):
    # 格式化成json, 并输出
    def jsonify(self, **args):
        data = dict(
            success=args.get('success', True),
            msg=args.get('msg', None),
            data=args.get('data', args),
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

@route("/api/get.form", allow=['admin'])
class GetForm(RequestHandler):

    '''取表单的结构'''
    @asynchronous
    @gen.engine
    def get(self):
        form_name = self.get_argument('form')
        if not form_name:
            self.jsonify(success=False, msg='Not Form Name')
            return

        locale_code = 'en_US'
        if hasattr(self, 'locale') and hasattr(self.locale, 'code'):
            locale_code = self.locale.code

        try:
            form_obj = import_object(form_name)(locale_code=locale_code)
        except Exception, e:
            self.jsonify(success=False, msg=str(e))
            return
        
        form_obj.xsrf_form_html = self.xsrf_form_html
        yield gen.Task(form_obj.load_field_data)
        form_obj.load_data(self.request.arguments)

        self.jsonify(form=form_obj.to_dict())

@route("/api/admin.route", allow=['admin'])
class AdminRoute(RequestHandler):
    '''后台路由'''

    def get(self):
        self.jsonify(data=admin_menu.list())

@admin_menu('system/me', is_show=False)
@route("/api/me", allow=['admin'])
class Me(RequestHandler):
    '''个人资料'''

    def get(self):
        print self.current_user
        pass
        

@admin_menu('content/category', title='分类管理')
@route("/api/category", allow=['admin'])
class Category(RequestHandler):

    @asynchronous
    @gen.engine
    def get(self):
        '''查看所有分类，包括停用的'''
        tree = yield gen.Task(cms.Category.td_tree, all_state=True)

        self.jsonify(data=tree)


    @validator('id', 'number') # 验证参数 id 是否为数字
    @validator('state', 'number', choices=(0,1))
    @asynchronous
    @gen.engine
    def put(self):
        '''停用/启用 分类'''
        if False == self._is_validated:
            self.jsonify(
                success=False,
                msg=self._validator_error['msg']
            )
            return
        
        # 检查分类是否存在
        category_ar = cms.Category.select()\
            .where(cms.Category.id == self.context['id'])

        if 0 == (yield gen.Task(category_ar.count)):
            self.jsonify(
                success=False,
                msg='not Data')
            return

        category_model = yield gen.Task(category_ar.get)
        category_model.state = self.context['state']
        yield gen.Task(category_model.save)

        self.jsonify()

    @form('app.forms.cms.Category')
    @asynchronous
    @gen.engine
    def post(self):
        yield gen.Task(self.form.load_field_data)

        if not self.form.validate():
            self.jsonify(
                success=False,
                msg=' \n '.join(self.format_form_error(self.form)))
            return

        post = self.form.data
              
        if post['id'] != '':
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

            if post['id'] != '':
                # 上级不能是自身及下级
                ids = [post['id']]
                for x in (yield gen.Task(cms.Category.get_childs, post['id'])):
                    ids.append(x['id'])
                category_ar = category_ar.where(~(cms.Category.id << ids))
            
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
            
            del post['id']
            category_model = cms.Category(**post)

            category_model.table = yield gen.Task(
                cms.Table.select().where(cms.Table.id == post['table']).get
            )

            yield gen.Task(category_model.save)
        else:
            
            #不能更改数据表
            if 'table' in self.form.data:
                del self.form.data['table']
            # category_model.table = yield gen.Task(
            #     cms.Table.select().where(cms.Table.id == post['table']).get
            # )
            
            self.form.data_to_model(category_model)

            yield gen.Task(category_model.save)
                    
        self.jsonify(data=category_model._data)
        

