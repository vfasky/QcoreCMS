#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date: 2013-09-04 11:51:39
# @Author: vfasky (vfasky@gmail.com)
# @Link: http://vfasky.com
# @Version: $Id$
from tornado import gen
from xcat.form import Form, validators, fields
from app.models import cms

class Table(Form):
    '''表属性'''
    id = fields.HiddenField()

    title = fields.TextField(
        '名称', [
            validators.Required(),
            validators.Length(min=2, max=100),
        ]
    )

    table = fields.TextField(
        '表名', [
            validators.Required(),
            validators.Length(min=2, max=50),
        ]
    )

class TableField(Form):
    '''表字段属性'''
    id = fields.HiddenField()
    
    table_id = fields.HiddenField(
        'table_id', [
            validators.Required()
        ]
    )

    field_choices = []
    for v in cms.TableField.fields:
        field_choices.append((v, v))

    field = fields.SelectField(
        'field',
        choices=field_choices,
    )

    ui = fields.SelectField(
        '表单ui',
        choices=[],
    )

    name = fields.TextField(
        'name', [
            validators.Required(),
            validators.Length(min=3, max=100),
        ]
    )

    label = fields.TextField(
        'label', [
            validators.Required(),
            validators.Length(min=3, max=20),
            validators.Regexp(r'[A-Za-z]', message='只容许字母')
        ]
    )

    list_data = fields.TextAreaField(
         '可选数据',
         description = 'label=val 这样的形式，一行一个'
    )

    filter_rule = fields.TextAreaField(
        '数据过滤',
        description = '一行一个, 默认支持: md5, trim, int, str'
    )

    validator_rule = fields.TextAreaField(
        '数据验证',
        description = '''一行一个, 默认支持: Email(), IPAddress(), 
          Length(1,10), NumberRange(1,10), Required(), 
          Regexp('[A-Za-z]'), URL(), AnyOf(), NoneOf()
        '''
    )

    tip = fields.TextField(
        '表单提示'    
    )

    null = fields.SelectField(
        '容许为空',
        choices=[
            ('1', '是'),
            ('0', '否'),
        ],
        default='1'
    )

    index = fields.SelectField(
        '创建索引',
        choices=[
            ('1', '是'),
            ('0', '否'),
        ],
        default='0'
    )

    unique = fields.SelectField(
        '唯一数据',
        choices=[
            ('1', '是'),
            ('0', '否'),
        ],
        default='0'
    )

    default = fields.TextField(
        '默认值'    
    )

    max_length = fields.TextField(
        '最大长度', [
            validators.NumberRange(1, 255)
        ],
        filters=[int],
        default=0
    )
    
    order = fields.TextField(
        '排序', [
            validators.NumberRange(0, 9999)
        ],
        filters=[int],
        default=0
    )

    @gen.engine
    def load_field_data(self, callback=None):
        ui_data = []
        for v in (yield gen.Task(cms.FieldUi.select().execute)):
            ui_data.append((v.id, v.desc))

        self.ui.choices = ui_data
        #self.ui.default = ui_data[0][0]

        callback and callback()


class Category(Form):
    '''分类表单'''
    id = fields.HiddenField()
    
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
        '数据表',
        choices=[],
    )

    @gen.engine
    def load_field_data(self, callback=None):
        tree = yield gen.Task(cms.Category.td_tree)
        data = [('0', 'root')]
        for v in tree:
            data.append((str(v['id']), '%s %s' % (v['icon'], v['title'])))
        self.parent.choices = data

        tables = yield gen.Task(cms.Table.select().execute)
        data = []
        for v in tables:
            data.append((str(v.id), v.title))
        self.table.choices = data

        callback and callback()
