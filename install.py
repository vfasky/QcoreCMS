#coding=utf-8
# 安装脚本
import sys
import os

# 设置系统编码为utf8
code = sys.getdefaultencoding()
if code != 'utf8':
	reload(sys)
	sys.setdefaultencoding('utf8')

version = '1.0 DEV'

# 是否创建数据库
createTable = False	

# 是否开发模式
isDev = False

# 数据库连接信息
host     = '127.0.0.1:3306' 
database = 'qcms' 
user     = 'root' 
password = '' 

# 监听端口
port = 8889



### 以下代码不修改 ###
import tornado.database
from YooYo.db.mySql import Database

path = os.path.dirname(__file__)

Database.addConnect(tornado.database.Connection(
	host = host,
	database = database ,
	user = user ,
	password = password 
))

if createTable :
	#print 'CREATE DATABASE `%s`;' % database
	Database.execute('CREATE DATABASE `%s`;' % database)

sqlFile = open(os.path.join(path,'qcms.sql') , 'r')	
sql = sqlFile.read()
sqlFile.close()

#print sql
print Database.execute(sql)

appTpl = '''
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
    'is_dev' : %s , 
    'session' : {
    	'left_time' : 3600 * 24 ,
    	'storage' : 'Memory'
    },
    'acl' : config.acl ,
    'login_url' : '/login',
    'version' : '%s' ,
    'ui_modules' : app.uimodules,
}

# 配置数据库连接
Database.addConnect(tornado.database.Connection(
	host = '%s' ,
	database = '%s' ,
	user = '%s' ,
	password = '%s' 
))

application = tornado.web.Application(config.routes,**settings)

application.listen(%s)
tornado.ioloop.IOLoop.instance().start()
''' % (
	isDev ,
	version ,
	host ,
	database ,
	user ,
	password ,
	port
)
#print appTpl
appFile = open( os.path.join(path , 'app.py') , 'w')
appFile.write(appTpl)
appFile.close()