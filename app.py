#coding=utf-8
import sys
import os

# 设置系统编码为utf8
code = sys.getdefaultencoding()
if code != 'utf8':
	reload(sys)
	sys.setdefaultencoding('utf8')

# 添加类搜索路径
app_path = os.path.dirname(__file__)
sys.path.append( os.path.join(app_path, 'app/module/') )

import tornado.ioloop
import tornado.database
import tornado.web

import YooYo.session
import app.config as config

from YooYo.db.mySql import Database

# ui_modules
import app.uimodules

# 设置
settings = {
    'debug': True,
    'gzip': True,
    'cookie_secret' : 'Qcms-by-fms',
    #'xsrf_cookies' : True,
    'static_path' : os.path.join(app_path, 'static'),
    'upload_path' : 'file',
    'template_path' : os.path.join(app_path, 'app/view'),
    'autoescape' : None ,
    'is_dev' : True , 
    'session' : {
    	'left_time' : 3600 * 24 ,
    	'storage' : 'Memory'
    },
    'acl' : config.acl ,
    'login_url' : '/login',
    'version' : '1.0.0-dev' ,
    'ui_modules' : app.uimodules,
}

# 配置数据库连接
if settings['is_dev']:
	Database.addConnect(tornado.database.Connection(
				host = '127.0.0.1:3306' ,
				database = 'qcms' ,
				user = 'root' ,
				password = '' 
			))
else:
	Database.addConnect(tornado.database.Connection(
				host = '127.0.0.1:3306' ,
				database = 'qcms' ,
				user = 'root' ,
				password = '' 
			))

application = tornado.web.Application(config.routes,**settings)

application.listen(8889)
tornado.ioloop.IOLoop.instance().start()
