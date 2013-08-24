#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2013-08-24 16:23:58
# @Author  : vfasky (vfasky@gmail.com)
# @Link    : http://vfasky.com
# @Version : $Id$

from xcat.web import RequestHandler, route 
from tornado import gen
from tornado.web import asynchronous

@route(r"/")
class Index(RequestHandler):
    """Home"""

    def get(self):
        self.write('hello QcoreCMS')