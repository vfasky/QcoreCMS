#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date: 2013-09-04 11:51:39
# @Author: vfasky (vfasky@gmail.com)
# @Link: http://vfasky.com
# @Version: $Id$
from tornado import gen
from xcat.form import Form, validators, fields
from app.models import cms

class CategoryAdd(Form):
    '''分类添加'''
    parent = fields.SelectField(
        '上级',
        choices=[],
    )

    title = fields.TextField(
        '名称', [
            validators.Required(),
            validators.Length(min=3, max=100),
        ]
    )
    
    desc = fields.TextField(
        '描述', [
            validators.Required(),
            validators.Length(min=3, max=255),
        ]
    )

    table = fields.SelectField(
        '数据模型',
        choices=[],
    )

    @gen.engine
    def load_field_data(self, callback=None):
        tables = yield gen.Task(cms.Table.select().execute)
        data = []
        for v in tables:
            data.append((str(v.id), v.title))
        self.table.choices = data

        tree = yield gen.Task(cms.Category.td_tree)
        data = [('0', 'root')]
        for v in tree:
            data.append((str(v['id']), '-%s %s' % (v['icon'], v['title'])))
        self.parent.choices = data

        callback and callback(self)

