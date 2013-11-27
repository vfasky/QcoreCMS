#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = [
    'Table',
    'FieldUi',
    'Category',
    'Content',
    'ContentData',
    'table_prefix',
]
import uuid
import xcat
from xcat import utils
from xcat import mopee, config
from tornado import gen
from app.models import AsyncModel, User

# 表前缀
table_prefix = 'cms_'

# 加载缓存 
cache = False
cache_cfg = config.get('cache', False)
cache_storage = cache_cfg.get('storage', 'Mongod')
if cache_cfg and hasattr(xcat.cache, cache_storage):
    Cache = getattr(xcat.cache, cache_storage)
    #print cache_cfg.get('config')
    cache = Cache(**cache_cfg.get('config', {}))


class Table(AsyncModel):
    """内容表列表"""

    # 模型定义缓存
    _model_caches = {}

    class Meta:
        db_table = '%s%s' % (table_prefix, 'table')

    title = mopee.CharField(max_length=100)
    table = mopee.CharField(max_length=80, unique=True)
    # 是否启用
    state = mopee.IntegerField(default=1, index=True)

    @classmethod 
    @gen.engine
    def sync(cls, table, callback, key=False):
        cls._model_caches.setdefault(table, {
            'key': 0,
            'model': False
        })

        if False == key:
            cls._model_caches[table]['model'] = False
            key = str(uuid.uuid4())
        


        if cache:
            # 通知 Table 更新 model 缓存
            cache_key = 'QcoreCMSModelCache%s' % table
            yield gen.Task(cache.set, cache_key, key)

        callback()

    @classmethod 
    @gen.engine
    def set_model_cache(cls, table, model, callback):
        def_val = {
            'key': 0,
            'model': False
        }
        cls._model_caches.setdefault(table, def_val)

        cache_data = cls._model_caches[table]

        cache_data['model'] = model
        cache_data['key'] = str(uuid.uuid4())

        yield gen.Task(cls.sync, table=table, key=cache_data['key'])

        callback()


    @classmethod 
    @gen.engine
    def get_model_cache(cls, table, callback):
        def_val = {
            'key': 0,
            'model': False
        }
        cls._model_caches.setdefault(table, def_val)

        cache_data = cls._model_caches[table]

        # 取同步信号
        if cache:
            cache_key = 'QcoreCMSModelCache%s' % table
            sync_key = yield gen.Task(cache.get, cache_key, 0)

            if sync_key == cache_data['key'] :
                callback(cache_data['model'])
            else:
                callback(False)
        else:
            callback(cache_data['model'])


    @property
    def full_name(self):
        return '%s%s' % (table_prefix, self.table)


    # 取索引模型
    def get_model(self):
        Clone = content_clone(self.table)
        return Clone

    # 取内容模型
    @gen.engine
    def get_data_model(self, callback):
        #print self.get_model_cache
        Model = yield gen.Task(self.get_model_cache, table=self.table)
        
        if Model:
            callback(Model)
            return

        Clone = ContentData.clone(self.table)

        ar = TableField.select().where(TableField.table == self)\
                       .order_by(TableField.order.desc())

        fields = yield gen.Task(ar.execute)

        for v in fields:
            if hasattr(mopee, v.field):
                field = getattr(mopee, v.field)(
                    default=v.default,
                    index=v.index,
                    null=v.null,
                    unique=v.unique
                )
                Clone.set_attr(v.name, field)

        Clone._fields_ar = fields

        yield gen.Task(self.set_model_cache, self.table, Clone)
        
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
    list_data = mopee.TextField(default='', help_text="列表数据")
    filters = mopee.CharField(default='', help_text="编辑数据时，对数据进行过滤的函数")
    validators = mopee.CharField(default='', help_text="编辑数据时，对数据进行验证的函数")
    tip = mopee.CharField(max_length=255, default='', help_text="编辑时的提示信息")
    null = mopee.IntegerField(max_length=2, default=1, help_text="1: 容许空 0: 否")
    index = mopee.IntegerField(max_length=2, default=0)
    unique = mopee.IntegerField(max_length=2, default=0)
    default = mopee.CharField(max_length=255, default=None, null=True)
    max_length = mopee.IntegerField(max_length=2, default=None, null=True)
    order = mopee.IntegerField(default=0, index=1)
    
    # 支持的过滤
    filter_func = ['int', 'str', 'float', 'trim', 'md5', 'sha1']
    # 支持的验证规则
    validator_rules = ['Email', 'IPAddress', 'Length', 
        'NumberRange', 'Required', 'Regexp', 'URL',
        'AnyOf', 'NoneOf']

    @classmethod
    def validators2str(cls, validator_arr):
        '''将验证规则转换成合法string'''
        rules = []
        for rule in validator_arr:
            args = []
            for r in rule['args']:
                if utils.Validators.is_number(r):
                    args.append(str(r))
                else:
                    args.append("'%s'" % r)

            arg_str = ', '.join(args)
            rule_name = '%s(%s)' % (rule['name'],  arg_str)

            rules.append(rule_name)

        return '\n'.join(rules)

    @classmethod
    def decode_validator(cls, validator_str):
        '''解码验证规则成数组'''
        if '' == validator_str.strip():
            return []

        clss = []

        lower_rules = []
        for rule in cls.validator_rules:
            lower_rules.append(rule.lower())

        for cls_str in validator_str.split('\n'):
            if -1 != cls_str.find('(') and -1 != cls_str.find(')'):
                tmp = cls_str.split('(')
                cls_name = tmp[0].strip()
                args = []
                if 2 == len(tmp):
                    args = tmp[1].strip(')').split(',')
                elif 2 < len(tmp):
                    arg_arr = []
                    for i in range(1, len(tmp)):
                        arg_arr.append(tmp[i])
                    arg_str = '('.join(arg_arr)
                    args = arg_str.strip(')').split(',')

                args2 = []
                for v in args:
                    v = v.strip()
                    if 0 == v.find("'"):
                        args2.append(v.strip("'"))
                    elif 0 == v.find('"'):
                        args2.append(v.strip('"'))
                    elif utils.Validators.is_number(v):
                        args2.append(int(v))
             
                if cls_name.lower() in lower_rules:
                    ix = lower_rules.index(cls_name.lower())
                    clss.append(dict(
                        name=cls.validator_rules[ix],
                        args=args2
                    ))

        return clss


    @classmethod
    def decode_filters(cls, filter_str):
        '''解码过滤规则成数组'''
        if '' == filter_str.strip():
            return []

        funcs = []
        for func_str in filter_str.split('\n'):
            func_str = func_str.strip()
            if func_str in cls.filter_func:
                funcs.append(func_str)

        return funcs

    @classmethod
    def filter2funcs(cls, filter_arr):
        '''将过滤规则转成func'''
        funcs = []
        for func_str in filter_arr:
            if 'int' == func_str:
                funcs.append(int)
            elif 'str' == func_str:
                funcs.append(str)
            elif 'float' == func_str:
                funcs.append(float)
            elif 'trim' == func_str:
                def trim(val):
                    return str(val).strip()
                funcs.append(trim)
            elif 'md5' == func_str:
                def md5(val):
                    return utils.md5(val) 
                funcs.append(md5)
            elif 'sha1' == func_str:
                def sha1(val):
                    return utils.sha1(val) 
                funcs.append(sha1)

        return funcs



class Category(AsyncModel):

    """内容分类表"""

    class Meta:
        db_table = '%s%s' % (table_prefix, 'category')

    title = mopee.CharField(max_length=100, unique=True)
    desc = mopee.CharField(max_length=255, null=True)

    # 分类关联的表
    table = mopee.ForeignKeyField(Table)
    # 父id
    parent = mopee.IntegerField(default=0, index=True)

    order = mopee.IntegerField(default=0, index=True)

    # 是否启用
    state = mopee.IntegerField(default=1, index=True)

    @classmethod
    @gen.engine
    def td_tree(cls, callback, all_state=False):
        '''返回二维树'''
        tree_list = yield gen.Task(cls.tree, all_state=all_state)
        td_tree_list = []

        def get_childs(item):
            v = item
            icon = [' -']
            for n in range(0, v['level']):
                icon.append(' -')

            v['icon'] = ''.join(icon)

            child_tree = v.pop('child_tree')
            td_tree_list.append(v)
            for c in child_tree:
                get_childs(c)

        for v in tree_list:
            get_childs(v)

        callback(td_tree_list)

    @classmethod
    @gen.engine
    def get_childs(cls, id, callback):
        '''取指定分类的下级'''
        td_tree = yield gen.Task(cls.td_tree, all_state=True)
        childs = []
        level = -1
        is_add = False
        for v in td_tree:
            if str(v['id']) == str(id):
                level = v['level']
                is_add = True
            elif level != -1 and is_add and v['level'] <= level:
                is_add = False
            elif level != -1 and is_add and v['level'] > level:
                childs.append(v)

        callback and callback(childs)

    @classmethod
    @gen.engine
    def tree(cls, callback, all_state=False):
        '''返回多维树'''
        ar = cls.select(
            cls.id, cls.parent,
            cls.title, cls.desc, cls.state,
            cls.table, Table.table
        ).join(Table).order_by(
            cls.order.desc()
        )

        # 返回所有状态
        if False == all_state:
            ar.where(cls.state == 1)

        data = yield gen.Task(ar.execute)

        all_tree = []
        root_tree = []

        for v in data:
            item = v._data
            item['table_name'] = v.table.table #'%s%s' % (table_prefix, v.table.table)

            all_tree.append(item)
            if item['parent'] == 0:
                root_tree.append(item)
                all_tree.remove(item)

        def get_childs(item):
            child_tree = 'child_tree' in item and item['child_tree'] or []
            for v in all_tree:

                if v['parent'] == item['id']:
                    v['level'] = item['level'] + 1
                    
                    if all_state and item['state'] == 0:
                        v['state'] = 0

                    v['child_tree'] = get_childs(v)

                    child_tree.append(v)

            return child_tree

        tree_list = []
        for v in root_tree:
            v['level'] = 0
            v['child_tree'] = get_childs(v)
            tree_list.append(v)

        callback(tree_list)


def content_clone(table):
    '''复制一个内容索引模型'''
    class Copy(AsyncModel):

        class Meta:
            db_table = '%s%s' % (table_prefix, table)
        """内容索引"""
        title = mopee.CharField(max_length=255, help_text='标题')
        slug = mopee.CharField(max_length=255, unique=True, help_text='页面名')
        desc = mopee.CharField(max_length=255, null=True, help_text='简介')
        created = mopee.IntegerField(help_text='创建时间')
        modified = mopee.IntegerField(null=True, help_text='修改时间')
        order = mopee.IntegerField(default=0, help_text='排序')
        user = mopee.ForeignKeyField(
            User, related_name='%s_user_id' % table, help_text='发布者')
        category = mopee.ForeignKeyField(
            Category, related_name='%s_category_id' % table, help_text='所属分类')
        # 0 下线 1 为发布 2 为草稿
        status = mopee.IntegerField(default=1, index=1, help_text='状态')
        # 1 为容许评论 0 为禁止
        allow_comment = mopee.IntegerField(default=1, help_text='是否容许评论')
    return Copy


class ContentData(AsyncModel):

    """内容动态扩展模型"""

    # 内容索引表 id
    parent_id = mopee.IntegerField(unique=True)

    @classmethod
    def set_attr(cls, key, field):
        field.add_to_class(cls, key)

    @classmethod
    @gen.engine
    def remove_field(cls, key, callback):
        sql = 'ALTER TABLE %s DROP COLUMN %s;' % (cls._meta.db_table, key)
        yield gen.Task(cls._meta.database.execute_sql, sql)
        
        yield gen.Task(Table.sync, cls._table)
        
        callback({
            'success': True
        })
        
    @classmethod
    @gen.engine
    def add_field(cls, key, field_str, callback, **kwargs):
        if hasattr(mopee, field_str):
            field = getattr(mopee, field_str)(**kwargs)
            field.add_to_class(cls, key)
            compiler = cls._meta.database.get_compiler()
            sql = 'ALTER TABLE %s ADD COLUMN %s;' % (
                cls._meta.db_table, compiler.field_sql(field))
            yield gen.Task(cls._meta.database.execute_sql, sql)
            
            yield gen.Task(Table.sync, cls._table)

            callback({
                'success': True
            })

            return

        callback({
            'success': False,
            'msg': 'field 不存在'
        })

    @staticmethod
    def clone(table):
        class Copy(ContentData):
            _table = table

            class Meta:
                db_table = '%s%s_data' % (table_prefix, table)
        return Copy
