#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = [
    'Table',
    'FieldUi',
    'Category',
    'Content',
    'ContentData',
] 
import re
from peewee import RelationDescriptor, ReverseRelationDescriptor
from xcat import mopee
from tornado import gen
from ..models import AsyncModel, User

# 表前缀
table_prefix = 'cms_'

class Table(AsyncModel):
    """内容表列表"""

    class Meta:
        db_table = '%s%s' % (table_prefix, 'table')

    title = mopee.CharField(max_length=100)
    table = mopee.CharField(max_length=80, unique=True)

    # 取索引模型
    def get_model(self):
        Clone = content_clone(self.table)
        return Clone

    # 取内容模型
    @gen.engine
    def get_data_model(self, callback):
        Clone = ContentData.clone(self.table)
    
        ar = TableField.select().where(TableField.table == self)\
                       .order_by(TableField.order.desc())

        fields = yield gen.Task(ar.execute)

        for v in fields:
            if hasattr(mopee, v.field):
                field = getattr(mopee, v.field)(
                    default = v.default,
                    index  = v.index,
                    null = v.null,
                    unique = v.unique
                )
                Clone.set_attr(v.name, field)

        callback(Clone)

class FieldUi(AsyncModel):
    """内容表UI"""

    class Meta:
        db_table = '%s%s' % (table_prefix, 'field_ui')

    name = mopee.CharField(max_length=100)
    plugin = mopee.CharField(max_length=255, null=True, help_text="ui 插件")
    desc = mopee.CharField(max_length=255, null=True)


class TableField(AsyncModel):
    """内容表结构定义"""

    class Meta:
        db_table = '%s%s' % (table_prefix, 'table_field')

    fields = (
        'BigIntegerField',
        'BlobField',
        'BooleanField',
        'CharField',
        'DateField',
        'DateTimeField',
        'DecimalField',
        'DoubleField',
        'FloatField',
        'IntegerField',
        'TextField',
        'TimeField',
    )

    table = mopee.ForeignKeyField(Table)
    ui = mopee.ForeignKeyField(FieldUi)
    field = mopee.CharField(choices=fields, max_length=100)
    name = mopee.CharField(max_length=100, help_text="字段名")
    label = mopee.CharField(max_length=100, help_text="表单名")
    list_data = mopee.TextField(default='[]', help_text="列表数据")
    filters = mopee.CharField(default='[]', help_text="编辑数据时，对数据进行过滤的函数")
    validators = mopee.CharField(default='[]', help_text="编辑数据时，对数据进行验证的函数")
    tip = mopee.CharField(max_length=255, default='', help_text="编辑时的提示信息")
    null = mopee.IntegerField(max_length=2, default=1, help_text="1: 容许空 0: 否") 
    index = mopee.IntegerField(max_length=2, default=0)
    unique = mopee.IntegerField(max_length=2, default=0)
    default = mopee.CharField(max_length=255, default=None, null=True)
    max_length = mopee.IntegerField(max_length=2,default=None, null=True)
    order = mopee.IntegerField(default=0, index=1)


class Category(AsyncModel):
    """内容分类表"""

    class Meta:
        db_table = '%s%s' % (table_prefix, 'category')

    title = mopee.CharField(max_length=100, unique=True)
    desc = mopee.CharField(max_length=255, null=True)

    # 分类关联的表
    table = mopee.ForeignKeyField(Table)
    # 父id
    parent = mopee.IntegerField(default=0,index=True) 

    # 祖先树
    parents = mopee.TextField(default=',0,')
    # 子孙树 -_-!
    childs  = mopee.TextField(default=',')

    order   = mopee.IntegerField(default=0,index=True)

def content_clone(table):
    '''复制一个内容索引模型'''
    class Copy(AsyncModel):
        class Meta:
            db_table = '%s%s' % (table_prefix, table)
        """内容索引"""
        title = mopee.CharField(max_length=255,help_text='标题')
        slug = mopee.CharField(max_length=255,unique=True,help_text='页面名')
        desc = mopee.CharField(max_length=255,null=True,help_text='简介')
        created = mopee.IntegerField(help_text='创建时间')
        modified = mopee.IntegerField(null=True,help_text='修改时间')
        order = mopee.IntegerField(default=0,help_text='排序')
        user = mopee.ForeignKeyField(User, related_name='%s_user_id' % table, help_text='发布者')
        category = mopee.ForeignKeyField(Category, related_name='%s_category_id' % table, help_text='所属分类')
        status = mopee.IntegerField(default=1, index=1, help_text='状态') #0 下线 1 为发布 2 为草稿
        # 1 为容许评论 0 为禁止
        allow_comment = mopee.IntegerField(default=1,help_text='是否容许评论')
    return Copy

class ContentData(AsyncModel):
    """内容动态扩展模型"""

    # 内容索引表 id
    parent_id = mopee.IntegerField(unique=True)
    
    @classmethod
    def set_attr(cls,key,field):
        field.add_to_class(cls,key)

    
    @classmethod
    @gen.engine
    def remove_field(cls, key, callback):
        sql = 'ALTER TABLE %s DROP COLUMN %s;' % (cls._meta.db_table, key)
        yield gen.Task(cls._meta.database.execute_sql, sql)
        callback({
            'success' : True
        })

    @classmethod
    @gen.engine
    def add_field(cls,key,field_str,callback,**kwargs):
        if hasattr(mopee,field_str):
            field = getattr(mopee,field_str)(**kwargs)
            field.add_to_class(cls, key)
            compiler = cls._meta.database.get_compiler()
            sql = 'ALTER TABLE %s ADD COLUMN %s;' % (cls._meta.db_table, compiler.field_sql(field))
            yield gen.Task(cls._meta.database.execute_sql, sql)
            callback({
                'success' : True
            })
            return
        
        callback({
            'success' : False ,
            'msg' : 'field 不存在'
        })

    @staticmethod
    def clone(table):
        class Copy(ContentData):
            class Meta:
                db_table = '%s%s_data' % (table_prefix, table)
        return Copy