#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2013-08-24 11:07:21
# @Author  : vfasky (vfasky@gmail.com)
# @Link    : http://vfasky.com
# @Version : $Id$

import sys
reload(sys)
sys.setdefaultencoding('utf8')

import os
from tornado.options import define, options, parse_command_line

# 定义参数
define('port', default=8888, type=int)
define('model', default='devel')
define('psycopg2_impl', default='psycopg2')

parse_command_line()

psycopg2_impl = options.psycopg2_impl

if psycopg2_impl == 'psycopg2cffi':
    from psycopg2cffi import compat
    compat.register()
elif psycopg2_impl == 'psycopg2ct':
    from psycopg2ct import compat
    compat.register()

from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from xcat import config
from xcat.web import Application
from config import settings


# 设置运行模式
settings['run_mode'] = options.model
config.load(settings)

# 连接数据库，长连接
config.get('database').connect()

# uimodules
from app import uimodules
config.set('ui_modules', uimodules)

if __name__ == '__main__':
    from app.handlers import *
    application = Application(**config.get())
    http_server = HTTPServer(application)
    http_server.listen(options.port)
    IOLoop.instance().start()
