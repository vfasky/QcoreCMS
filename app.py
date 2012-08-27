#coding=utf-8
import sys
import os

# 设置系统编码为utf8
code = sys.getdefaultencoding()
if code != 'utf8':
	reload(sys)
	sys.setdefaultencoding('utf8')


import config
import tornado.ioloop
import tornado.database
import tornado.web

from YooYo.db.mySql import Database

# 添加类搜索路径
sys.path.append( os.path.join(config.app_path, 'app/module/') )

# 连接数据库
database = config.settings['database'][ config.settings['run_mode'] ]
Database.addConnect(tornado.database.Connection(
    host = database['host'],
    database = database['database'] ,
    user = database['user'] ,
    password = database['password']
))

# run app
application = tornado.web.Application(config.routes,**config.settings)
application.listen(config.settings['port'])
tornado.ioloop.IOLoop.instance().start()
