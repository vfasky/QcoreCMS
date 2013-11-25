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
    @validator('form')
    @asynchronous
    @gen.engine
    def get(self):
        '''停用/启用 分类'''
        if False == self.validator.success:
            self.jsonify(
                success=False,
                msg=self.validator.error.msg,
            )
            return

        form_name = self.validator.data.form
        if form_name.find('app.') != 0 or form_name.find('..') != -1:
            self.jsonify(success=False, msg='Not Form Name')
            return

        locale_code = 'en_US'
        if hasattr(self, 'locale') and hasattr(self.locale, 'code'):
            locale_code = self.locale.code


        form_obj = import_object(form_name)(locale_code=locale_code)

        #try:
            #form_obj = import_object(form_name)(locale_code=locale_code)
        #except Exception, e:
            #self.jsonify(success=False, msg=str(e))
            #return
        
        form_obj.xsrf_form_html = self.xsrf_form_html
        yield gen.Task(form_obj.load_field_data)
        form_obj.load_data(self.request.arguments)

        self.jsonify(form=form_obj.to_dict())

@admin_menu('system/me', is_show=False)
@route("/api/me", allow=['admin'])
class Me(RequestHandler):
    '''个人资料'''

    def get(self):
        print self.current_user
        pass
    
@admin_menu('content/tablefield', uri='/content/tablefield/:id', is_show=False)
@route("/api/tablefield", allow=['admin'])
class TableField(RequestHandler):
    # 表字段管理
    
    @asynchronous
    @gen.engine
    @validator('id', 'number')
    def get(self):
        if False == self.validator.success:
            self.jsonify(
                success=False,
                msg=self.validator.error.msg 
            )
            return

        id = self.validator.data.id

        table = cms.Table.select().where(cms.Table.id == id)

        if 0 == (yield gen.Task(table.count)):
            self.jsonify(
                success=False,
                msg='No Data'
            )
            return

        table_ar = yield gen.Task(table.get)
        ContentModel = yield gen.Task(table_ar.get_data_model)

        data = []
        for v in ContentModel._fields_ar:
            field = v._data
            if not field.get('fieldUI'):
                field['fieldUI'] = (yield gen.Task(
                        cms.FieldUi.select().where(cms.FieldUi.id == field['ui']).get
                ))._data
            data.append(field)

        self.jsonify(data=dict(
            table=table_ar.table,
            data=data,
        ))

    @asynchronous
    @gen.engine
    @validator('id', 'number')
    @validator('label')
    def put(self):
        if False == self.validator.success:
            self.jsonify(
                success=False,
                msg=self.validator.error.msg 
            )
            return

        put = self.validator.data

        field_ar = cms.TableField.select(cms.TableField, cms.Table.table).where(
                cms.TableField.id == put.id
        ).join(cms.Table)

        if 0 == (yield gen.Task(field_ar.count)):
            self.jsonify(
                success=False,
                msg='No Data'
            )
            return

        field_ar = yield gen.Task(field_ar.get)

        field_ar.label = put.label
        yield gen.Task(field_ar.save)
        yield gen.Task(cms.Table.sync, field_ar.table.table)

        self.jsonify()

@admin_menu('content/table', title='表管理')
@route("/api/table", allow=['admin'])
class Table(RequestHandler):
    #TODO 表暂不支持删除

    @asynchronous
    @gen.engine
    def get(self):
        table = yield gen.Task(cms.Table.select().execute)

        data = []
        for v in table:
            item = v._data
            item['full_name'] = v.full_name
            data.append(item)

        self.jsonify(data=data)

    @form('app.forms.cms.Table')
    @asynchronous
    @gen.engine
    def post(self):
        # 修改/ 添加表 注： 修改时，table 属性不能修改
        # 添加时，要动态创建表
        if not self.form.validate():
            self.jsonify(
                success=False,
                msg=' \n '.join(self.format_form_error(self.form)))
            return

        post = self.form.data
              
        if post['id'] == '':
            # 检查表是否已存在
            table_count = yield gen.Task(
                cms.Table.select().where(cms.Table.table == post['table']).count
            )

            if 0 != table_count:
                self.jsonify(
                    success=False,
                    msg='Table already exists'
                )
                return

            # 保存
            table_ar = cms.Table()
            table_ar.table = post['table']
            table_ar.title = post['title']
            yield gen.Task(table_ar.save)

            # 创建实例表
            Model = table_ar.get_model()
            exists = yield gen.Task(Model.table_exists)
            if not exists:
                yield gen.Task(Model.create_table)

            # 表默认字段
            field_base_data = {
                'ui': (yield gen.Task(
                    cms.FieldUi.select().where(cms.FieldUi.name == 'textarea')
                                        .where(cms.FieldUi.plugin == 'editor')
                                        .get
                )),
                'field': 'TextField',
                'name': 'content',
                'label': '内容',
            }

            table_field = cms.TableField(**field_base_data)
            table_field.table = table_ar
            yield gen.Task(table_field.save)

            #创建扩展表
            ExtModel = yield gen.Task(table_ar.get_data_model)
            exists = yield gen.Task(ExtModel.table_exists)
            if not exists:
                yield gen.Task(ExtModel.create_table)

            self.jsonify()
            return

        else:

            # 修改表，只能改表名
            table_ar = cms.Table.select().where(cms.Table.id == post['id'])

            if 0 == (yield gen.Task(table_ar.count)):
                self.jsonify(
                   success=False,
                   msg='not Data',
                )
                return

            table_ar = yield gen.Task(table_ar.get)
            table_ar.title = post['title']
            yield gen.Task(table_ar.save)

            self.jsonify()


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
        if False == self.validator.success:
            self.jsonify(
                success=False,
                msg=self.validator.error.msg,
            )
            return

        put = self.validator.data
        
        # 检查分类是否存在
        category_ar = cms.Category.select()\
            .where(cms.Category.id == put.id)

        if 0 == (yield gen.Task(category_ar.count)):
            self.jsonify(
                success=False,
                msg='not Data')
            return

        category_model = yield gen.Task(category_ar.get)
        category_model.state = put.state
        yield gen.Task(category_model.save)

        self.jsonify()

    @form('app.forms.cms.Category')
    @asynchronous
    @gen.engine
    def post(self):
        #TODO 修改名称时，检查名称是否重复
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
        

