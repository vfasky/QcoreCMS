#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2013-088888888-27 16:47:02
# @Author  : vfasky (vfasky@gmail.com)
# @Link    : http://vfasky.com
# @Version : $Id$

__all__ = [
    'BaseTest',
]

from tornado.testing import AsyncTestCase

class BaseTest(AsyncTestCase):
    def __init__(self, *args, **kwargs):
        self.assert_equal = self.assertEqual
        self.assert_raises = self.assertRaises
        self.assert_is_instance = lambda object, classinfo: self.assertTrue(isinstance(object, classinfo))
        super(BaseTest, self).__init__(*args, **kwargs)

    def setUp(self):
        super(BaseTest, self).setUp()
        self.set_up()

    def tearDown(self):
        self.tear_down()
        super(BaseTest, self).tearDown()

    def set_up(self):
        pass

    def tear_down(self):
        pass

    def stop_callback(self, result, error):
        self.stop((result, error))

    def run_gen(self, func):
        func()
        self.wait()

    def wait_for_result(self):
        cursor, error = self.wait()
        if error:
            raise error
        return cursor