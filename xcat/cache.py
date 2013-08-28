#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date: 2013-05-10 09:55:54
# @Author: vfasky (vfasky@gmail.com)
# @Version: $Id$
__all__ = ['Memcache', 'Mongod']

'''
    缓存
'''
import time
import asyncmemcache
from tornado import gen


'''
基于 memcache 的异步缓存
========================

'''
class Memcache(object):

    _conn = None

    def __init__(self, **kwargs):
        if not kwargs.get('servers', False):
            raise NameError, 'servers syntax'

        if not self._conn:
            self._conn = asyncmemcache.ClientPool(
                kwargs['servers'],
                maxclients = int(kwargs.get('maxclients', 100))
            )

    @gen.engine
    def get(self, key, default=None, callback=None):
        ret = yield gen.Task(self._conn.get, key)
        if ret is None:
            callback(default)
        else:
            callback(ret)

    @gen.engine
    def set(self, key, val, left_time=0, callback=None):
        ret = yield gen.Task(self._conn.set, key, val, left_time)
        if callback:
            callback(ret)

    @gen.engine
    def remove(self, key, callback=None):
        ret = yield gen.Task(self._conn.delete, key)
        if callback:
            callback(ret)



'''
基于 asyncmongo 的异步缓存
============================

## demo:

``` python

mongod = Mongod()

class Handler(RequestHandler):
    @asynchronous
    @gen.engine
    def get(self):
        # 写缓存, 缓存有效期，1小时
        ret = yield gen.Task(mongod.set, 'test2', {'hello': 'word'}, 3600)
        print ret
        # 读缓存
        data = yield gen.Task(mongod.get, 'test2')
        print data 
        # 删缓存
        ret = yield gen.Task(mongod.remove, 'test2')
        print ret

```

'''
try:
    import asyncmongo
except Exception, e:
    pass

class Mongod(object):

    def __init__(self, **kwargs):
        self._conn = asyncmongo.Client(
            pool_id = kwargs.get('pool_id', 'xcat.cache.Mongod'), 
            host = kwargs.get('host', '127.0.0.1'), 
            port = kwargs.get('port', 27017), 
            maxcached = kwargs.get('maxcached', 10), 
            maxconnections = kwargs.get('maxconnections', 50), 
            dbname = kwargs.get('dbname', 'cache'),
            dbuser = kwargs.get('dbuser', None),
            dbpass = kwargs.get('dbpass', None)
        )

        self._table = kwargs.get('table', 'caches')

    def get(self, key, default=None, callback=None):
        def _callback(data, error):
            if error:
                raise Error(error)
            if data:
                last_time = int(data['update_time']) + int(data['left_time'])

                if int(data['left_time']) == -1 or int(time.time()) <= last_time:       
                    return callback(data['val'])
                else:
                    self.remove(key)

            callback(default)

        self._conn[self._table].find_one({'key': key}, callback=_callback)    

    @gen.engine
    def set(self, key, val, left_time=-1, callback=None):
        def _callback(data, error):
            if error:
                raise Error(error)

            if callback:
                callback(len(data) == 1)

        ret, error = yield gen.Task(self._conn[self._table].find_one, {'key': key})
        data = ret[0]
        if not data or len(data) == 0:
            self._conn[self._table].insert({
                'key' : key,
                'val' : val,
                'left_time' : int(left_time),
                'update_time' : int(time.time()), 
            }, callback=_callback)
        else:
            self._conn[self._table].update({
                '_id' : data['_id']
            },{
                'key' : key,
                'val' : val,
                'left_time' : int(left_time),
                'update_time' : int(time.time()), 
            }, upsert=True, safe=True, callback=_callback)

    def remove(self, key, callback=None):
        def _callback(data, error):
            if error:
                raise Error(error)

            if callback:
                callback(len(data) == 1)

        self._conn[self._table].remove({
            'key' : key
        }, callback=_callback)

# 测试
if __name__ == '__main__':
    import unittest
    from test import BaseTest
    class MemcacheTest(BaseTest):
        '''asyncmemcache Test'''

        def set_up(self):
            self.cache = Memcache(servers=['127.0.0.1:11211'])

        def test_set_val(self):
            '''缓存文本'''
            self.cache.set('test_set_val', 'ok', callback=self.stop_callback)
            result = self.wait_for_result()
            self.assert_equal(result, None)

            self.cache.get('test_set_val', callback=self.stop_callback)
            result = self.wait_for_result()
            self.assert_equal(result, 'ok')

            self.cache.remove('test_set_val', callback=self.stop_callback)
            self.wait()
            self.cache.get('test_set_val', callback=self.stop_callback)
            result = self.wait_for_result()
            self.assert_equal(result, None)

        def test_set_obj_val(self):
            '''缓存对象'''
            obj_val = {'test': 1}
            self.cache.set('test_set_obj_val', obj_val, callback=self.stop_callback)
            result = self.wait_for_result()
            self.assert_equal(result, None)

            self.cache.get('test_set_obj_val', callback=self.stop_callback)
            result = self.wait_for_result()
            self.assert_equal(result, obj_val)

            self.cache.remove('test_set_obj_val', callback=self.stop_callback)
            self.wait()
            self.cache.get('test_set_obj_val', callback=self.stop_callback)
            result = self.wait_for_result()
            self.assert_equal(result, None)

    unittest.main()
 