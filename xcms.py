#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2013-08-24 11:07:21
# @Author  : vfasky (vfasky@gmail.com)
# @Link    : http://vfasky.com
# @Version : $Id$

import os
import sys
reload(sys)
sys.setdefaultencoding('utf8')

from tornado.options import define, options, parse_command_line
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from xcat import config
from xcat.web import Application
from config import settings

# 定义参数
define('port', default=80, type=int)
define('model', default='devel')
parse_command_line()

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
