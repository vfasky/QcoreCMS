#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date: 2013-05-10 14:36:13
# @Author: vfasky (vfasky@gmail.com)
# @Version: $Id$

'''
session
'''

__all__ = [
    'Base',
    'Mongod',
    'Memcache',
]

import uuid
import time
import cache

from tornado import gen


class Base(object):

    '''
    异步 session 基类
    '''

    def __init__(self, session_id=False, **settings):
        if False == session_id:
            session_id = str(uuid.uuid4())

        self.settings = settings
        self.session_id = session_id
        self.left_time = int(settings.get('left_time', 1800))
        self.storage = self.get_storage()
        self._data = {}

    @property
    def id(self):
        # 返回 session id
        return self.session_id

    def get_storage(self):
        pass

    @gen.engine
    def get_all(self, callback):
        data = yield gen.Task(self.storage.get)
        if not data:
            callback({})
            return

        this_time = int(time.time())
        cache_life = data.get('time', 0) + self.left_time
        if cache_life < this_time:
            # 缓存已经失效
            yield gen.Task(self.clear)
            callback({})
            return
        elif (cache_life - this_time) > (self.left_time / 2):
            # 缓存周期已经超过生存周期的一半，更新时间周期
            session = data.get('data', {})
            yield gen.Task(self.storage.set, session)

        else:
            session = data.get('data', {})

        callback(session)

    @gen.engine
    def set(self, key, value, callback=None):
        self._data = yield gen.Task(self.get_all)
        self._data[key] = value
        self.storage.set(self._data, callback)

    @gen.engine
    def get(self, key, default=None, callback=None):
        self._data = yield gen.Task(self.get_all)
        callback(self._data.get(key, default), None)

    @gen.engine
    def remove(self, key, callback=None):
        self._data = yield gen.Task(self.get_all)

        if self._data.has_key(key):
            del self._data[key]
            self.storage.set(self._data, callback)
        else:
            callback(False)

    def clear(self, callback=None):
        self.storage.remove(callback)


class Memcache(Base):

    """"基于Memcache的session"""

    class Storage(object):

        def __init__(self, conn, session_id, left_time):
            self._conn = conn
            self.session_id = session_id
            self.left_time = int(left_time)

        @gen.engine
        def get(self, callback=None):
            ret = yield gen.Task(self._conn.get, self.session_id, {})
            if callback:
                callback(ret)

        def remove(self, callback=None):
            self._conn.remove(self.session_id, callback=callback)

        @gen.engine
        def set(self, value, callback=None):
            session_data = {
                'data': value,
                'time': int(time.time())
            }
            ret = yield gen.Task(self._conn.set, self.session_id, session_data, self.left_time)
            if callback:
                callback(ret)

    def get_storage(self):
        conn = cache.Memcache(**self.settings)
        return self.Storage(conn, self.session_id, self.left_time)

try:
    import asyncmongo
except Exception, e:
    pass


class Mongod(Base):

    """"基于Mongod的session"""

    class Storage(object):

        def __init__(self, conn, table, session_id, left_time):
            self._conn = conn
            self._table = self._conn[table]
            self.session_id = session_id
            self.left_time = left_time
            self.where = {'session_id': session_id}

        def get(self, callback=None):
            def _callback(value, error):
                if callback:
                    if error:
                        raise Error(error)
                    if value:
                        callback(value)
                    else:
                        callback(None)

            self._table.find_one(self.where, callback=_callback)

        def remove(self, callback=None):
            def _callback(data, error):
                if callback:
                    if error:
                        raise Error(error)

                    if callback:
                        callback(len(data) == 1)

            self._table.remove(self.where, callback=_callback)

        @gen.engine
        def set(self, value, callback=None):
            session_data = {
                'session_id': self.session_id,
                'data': value,
                'time': int(time.time())
            }

            def _callback(data, error):
                if callback:
                    if error:
                        raise Error(error)

                    if callback:
                        callback(session_data)

            ret, error = yield gen.Task(self._table.find_one, self.where)
            data = ret[0]

            if not data or len(data) == 0:
                self._table.insert(session_data, callback=_callback)
            else:
                self._table.update({
                    '_id': data['_id']
                }, session_data, upsert=True, safe=True, callback=_callback)

    def get_storage(self):
        kwargs = self.settings
        conn = asyncmongo.Client(
            pool_id=kwargs.get('pool_id', 'xcat.session.Mongod'),
            host=kwargs.get('host', '127.0.0.1'),
            port=kwargs.get('port', 27017),
            maxcached=kwargs.get('maxcached', 10),
            maxconnections=kwargs.get('maxconnections', 50),
            dbname=kwargs.get('dbname', 'session'),
            dbuser=kwargs.get('dbuser', None),
            dbpass=kwargs.get('dbpass', None)
        )

        table = kwargs.get('table', 'sessions')

        return self.Storage(conn, table, self.session_id, self.left_time)

# 测试
if __name__ == '__main__':
    import unittest
    from test import BaseTest

    class MemcacheTest(BaseTest):

        '''asyncmemcache Test'''

        def set_up(self):
            self.session = Memcache(
                'test_session_key', servers=['127.0.0.1:11211'])

        def test_set_get_val(self):
            obj_val = {'test': 1}
            self.session.set(
                'test_set_obj_val', obj_val, callback=self.stop_callback)
            result = self.wait_for_result()
            self.assert_equal(result, None)
            
            self.session.get('test_set_obj_val', callback=self.stop_callback)
            result = self.wait_for_result()
            self.assert_equal(result, obj_val)

        def test_time_out(self):
            import time
            session = Memcache(
                'session_time_out_key', 
                left_time=2,
                servers=['127.0.0.1:11211'])
            obj_val = {'test': 1}
            session.set(
                'test_set_obj_val', obj_val, callback=self.stop_callback)
            result = self.wait_for_result()
            self.assert_equal(result, None)

            session.get('test_set_obj_val', callback=self.stop_callback)
            result = self.wait_for_result()
            self.assert_equal(result, obj_val)
            time.sleep(4)
            session.get('test_set_obj_val', callback=self.stop_callback)
            result = self.wait_for_result()
            self.assert_equal(result, None)

        def test_remove(self):
            obj_val = {'test': 1}
            self.session.set(
                'test_remove_val', obj_val, callback=self.stop_callback)
            result = self.wait_for_result()
            self.assert_equal(result, None)
            self.session.remove('test_remove_val', callback=self.stop)
            self.wait()
            self.session.get('test_remove_val', callback=self.stop_callback)
            result = self.wait_for_result()
            self.assert_equal(result, None)
            
        def test_clear(self):
            obj_val = {'test': 1}
            self.session.set(
                'test_clear_val', obj_val, callback=self.stop_callback)
            result = self.wait_for_result()
            self.assert_equal(result, None)
            self.session.clear(callback=self.stop)
            self.wait()
            self.session.get('test_clear_val', callback=self.stop_callback)
            result = self.wait_for_result()


    unittest.main()
'''
if __name__ == '__main__':
    from tornado.ioloop import IOLoop
    from tornado.httpserver import HTTPServer
    from tornado.web import asynchronous, RequestHandler, Application

    class Handler(RequestHandler):

        def initialize(self):
            key = 'PYSESSID'
            
            if self.get_secure_cookie(key):
                self.session = Memcache(self.get_secure_cookie(key), servers=['127.0.0.1:11211'])
            else:
                session = Memcache(str(uuid.uuid4()), servers=['127.0.0.1:11211'])
                self.set_secure_cookie(key , session.id)
                self.session = session
            

        @asynchronous
        @gen.engine
        def get(self):
            ret = yield gen.Task(self.session.set, 'test2', {'hello': 'word'})
            print ret
            data = yield gen.Task(self.session.get, 'test2')
            print data 
            ret = yield gen.Task(self.session.remove, 'test2')
            print ret
            ret = yield gen.Task(self.session.clear)
            print ret
            self.write('test')

            self.finish()
            
    application = Application([
        (r'/', Handler),
    ], debug=True, cookie_secret="fsfwo#@(sfk")

    http_server = HTTPServer(application)
    http_server.listen(8181)
    IOLoop.instance().start()
'''
