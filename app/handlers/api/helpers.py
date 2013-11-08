#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date: 2013-11-08 10:21:53
# @Author: vfasky (vfasky@gmail.com)
# @Link: http://vfasky.com
# @Version: $Id$

__all__ = [
    'admin_menu',
]

class AdminMenu(object):
    '''后台菜单助手'''

    # 用于存放菜单
    _list = {}

    def __init__(self, path, **args):
        self.path = path
        self.args = args

    def __call__(self, handler_class):
        self.add(self.path, **self.args)
        return handler_class


    @classmethod
    def reset(cls):
        cls._list = {} 

    @classmethod
    def add(cls, path, **args):
        paths = path.split('/')
        node = cls._list
        name = paths.pop()
        name = name == '' and 'index' or name

        attr = dict(
            _order=args.get('order', 0),
            _js=args.get('ctrl', 'admin/ctrls/%s' % name),
            _tpl=args.get('tpl', '/static/js/admin/tpls/%s.html' % name),
            _title=args.get('title', name),
            _uri=args.get('uri', '/%s' % path),
            _is_ctrl=args.get('is_ctrl', True),
            _path=path.replace('/', '_'),
            _name=name,
        )

        
        for p in paths:
            if p in node:
                node = node.get(p)
            else:
                node[p] = {}
                node = node[p]

        if name in node:
            attr.update(node[name])
            
        node[name] = attr

        return cls._list

    @classmethod
    def list(cls):
        routes = []
        def get_menu(data):
            keys = ('_order', '_js', '_tpl', '_uri', '_path',
                    '_title', '_name', '_is_ctrl')
            menu = []
            
            for v in data:
                if v not in keys:
                    item = dict(
                        name=v,
                        title=v,
                        order=0,
                        uri='',
                        is_ctrl=False,
                        child=[]
                    )

                    for k in keys:
                        key = k.strip('_')
                
                        if k in data[v]:
                            item[key] = data[v][k]

                    if item['is_ctrl']:
                        routes.append(dict(
                            js=item['js'],
                            uri=item['uri'],
                            tpl=item['tpl'],
                            name=item['path'],
                        ))

                    item['child'] = get_menu(data[v])
                    menu.append(item)

            return sorted(menu, key=lambda x:x['order'], reverse=True) 

        return dict(
           menu = get_menu(cls._list),
           routes = routes,
        )

# 别名
admin_menu = AdminMenu


# 测试
if __name__ == '__main__':
    
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '../../../'))
    
    import unittest
    from xcat.test import BaseTest
      
    class MenuTest(BaseTest):

        def test_add(self):
            result = AdminMenu.add('test/admin')

            self.assert_equal(
                result['test']['admin']['_ctrl'], 
                'admin/ctrls/adminCtrl')

            result = AdminMenu.add('test/admin2', title='test', order=100)

            self.assert_equal(
                result['test']['admin2']['_title'], 
                'test')
        
            result = AdminMenu.add('test', title='test0')

            self.assert_equal(
                result['test']['_title'], 
                'test0')


        def test_list(self):
            menu = AdminMenu.list()
            
            self.assert_equal(menu[0]['title'], 'test0')
            self.assert_equal(menu[0]['child'][0]['order'], 100)



    unittest.main()
