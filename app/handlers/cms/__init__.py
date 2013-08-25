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
    def creat_tables(self, keys, class_list, callback=None):
        for v in keys:
            if hasattr(class_list, v):
                model = getattr(class_list, v)
                exists = yield gen.Task(model.table_exists) 
                if not exists:
                    yield gen.Task(model.create_table) 

        if callback:
            callback(True)

    @gen.engine
    def creat_model(self, table, title, callback):
        # 默认模型定义
        field_base_data = {
           'ui' : (yield gen.Task(
                cms.FieldUi.select().where(cms.FieldUi.name == 'textarea')\
                                    .where(cms.FieldUi.plugin == 'editor')\
                                    .get
            )),
           'field' : 'TextField',
           'name': 'content',
           'label': '内容', 
        }
        
        model_table_ar = cms.Table.select().where(cms.Table.table == table)

        # 创建模型
        model_count = yield gen.Task(model_table_ar.count)
        if 0 == model_count:
            model_table = cms.Table()
            model_table.table = table
            model_table.title = title
            yield gen.Task(model_table.save)

            # 创建模型定义
            table_field = cms.TableField(**field_base_data)
            table_field.table = model_table
            yield gen.Task(table_field.save)
            
            # 创建模型
            model_model = model_table.get_model()
            exists = yield gen.Task(model_model.table_exists) 
            if not exists:
                yield gen.Task(model_model.create_table)

            # 创建扩展模型
            model_ext_model = yield gen.Task(model_table.get_data_model)
            exists = yield gen.Task(model_ext_model.table_exists) 
            if not exists:
                yield gen.Task(model_ext_model.create_table)
        else:
            model_table = yield gen.Task(model_table_ar.get)

        callback(model_table)



    @asynchronous
    @gen.engine
    def get(self):
        base = ('User', 'Role', 'UserRole')
        cms_base = ('Table', 'FieldUi', 'TableField', 'Category')

        yield gen.Task(self.creat_tables, base, models)

        yield gen.Task(self.creat_tables, cms_base, cms)

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

        # 创建 field ui
        ui_count = yield gen.Task(cms.FieldUi.select().count)
        if 0 == ui_count:
            ui_list = [
                {'name': 'input', 'desc': '单行文本'},
                {'name': 'radio', 'desc': '单选'},
                {'name': 'checkbox', 'desc': '多选'},
                {'name': 'select', 'desc': '下拉'},
                {'name': 'textarea', 'desc': '多行文本'},
                {'name': 'textarea', 'desc': '富文本编辑器', 'plugin': 'editor'},
                {'name': 'input', 'desc': '隐藏值', 'plugin': 'hidden'},
                {'name': 'input', 'desc': '图片上传', 'plugin': 'image_upload'},
                {'name': 'textarea', 'desc': '组图上传', 'plugin' : 'images_upload'},
                {'name': 'input', 'desc': '文件上传', 'plugin': 'file_upload'},
            ] 
            for v in ui_list:
                field_ui = cms.FieldUi(**v)
                yield gen.Task(field_ui.save)

        # 创建 page 模型
        page_table = yield gen.Task(self.creat_model, 'page', '单页面')

        # 创建 资讯 模型
        news_table = yield gen.Task(self.creat_model, 'news', '资讯')

        # 创建默认分类
        category_count = yield gen.Task(cms.Category.select().count)

        if 0 == category_count:
            # 创建 单页面 分类
            page_category = cms.Category()
            page_category.title = 'page'
            page_category.desc = '单页面'
            page_category.table = page_table
            yield gen.Task(page_category.save)

            # 创建 资讯 分类
            news_category = cms.Category()
            news_category.title = 'news'
            news_category.desc = '资讯'
            news_category.table = news_table
            yield gen.Task(news_category.save)



        self.write('ok')
        self.finish()

          