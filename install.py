#coding=utf-8
# 安装脚本

# 版本
version = '1.0 DEV'

# 是否创建数据库
create_database = False	

# 运行模式
run_mode = 'devel'
debug = True

# 数据库连接信息
host     = '127.0.0.1:3306' 
database = 'qcms' 
user     = 'root' 
password = '' 

# 监听端口
port = 8889

###### 以下代码不修改 ######
import sys
import os

# 设置系统编码为utf8
code = sys.getdefaultencoding()
if code != 'utf8':
	reload(sys)
	sys.setdefaultencoding('utf8')

import tornado.database
from YooYo.db.mySql import Database

path = os.path.dirname(__file__)

Database.addConnect(tornado.database.Connection(
	host = host,
	database = database ,
	user = user ,
	password = password 
))

if create_database :
	#print 'CREATE DATABASE `%s`;' % database
	Database.execute('CREATE DATABASE `%s`;' % database)

sqlFile = open(os.path.join(path,'qcms.sql') , 'r')	
sql = sqlFile.read()
sqlFile.close()

#print sql
print Database.execute(sql)

configTpl = '''
#coding=utf-8
import os

# 控制器
import app.controller.default
import app.controller.admin

# ui_modules
import app.uimodules

# 路由规则
routes = [
    (r"/", app.controller.default.index),
    (r"/PIE.htc", app.controller.default.PIE),

    (r"/login", app.controller.admin.login),
    (r"/logout", app.controller.admin.logout),

    (r"/admin", app.controller.admin.index),
    (r"/admin/content", app.controller.admin.content),
    (r"/admin/content-add-(\d+)$", app.controller.admin.contentAdd),
    (r"/admin/content-edit-(\d+)-(\d+)-(\d+)$", app.controller.admin.contentEdit),
    (r"/admin/content-(\d+)$", app.controller.admin.contentList),

    (r"/admin/role", app.controller.admin.role),
    (r"/admin/locale", app.controller.admin.locale),
    (r"/admin/user", app.controller.admin.user),

    (r"/admin/model", app.controller.admin.models),
    (r"/admin/model-field-(\d+)$", app.controller.admin.model_field),

    (r"/admin/category", app.controller.admin.category),

    (r"/admin/uploadFile", app.controller.admin.uploadFile),
    
    (r"/(.+)$", app.controller.default._404),
]

\'\'\'
访问规则
=================

特殊标识: 

 - ACL_NO_ROLE 没有角色用户
 - ACL_HAS_ROLE 有角色用户
 
\'\'\'
acl = {
    'app.controller.admin.index' : {
        'allow' : ['admin']
    },
    'app.controller.admin.role' : {
        'allow' : ['admin']
    },
    'app.controller.admin.locale' : {
        'allow' : ['admin']
    },
    'app.controller.admin.models' : {
        'allow' : ['admin']
    },
    'app.controller.admin.model_field' : {
        'allow' : ['admin']
    },
    'app.controller.admin.category' : {
        'allow' : ['admin']
    },
    'app.controller.admin.user' : {
        'allow' : ['admin']
    },
    'app.controller.admin.content' : {
        'allow' : ['admin']
    },
    'app.controller.admin.contentList' : {
        'allow' : ['admin']
    },
    'app.controller.admin.contentAdd' : {
        'allow' : ['admin']
    },
    'app.controller.admin.contentEdit' : {
        'allow' : ['admin']
    },
    'app.controller.admin.uploadFile' : {
        'allow' : ['admin']
    },
    'app.controller.admin.logout' : {
        'allow' : ['ACL_HAS_ROLE']
    },
}

# 项目根目录
app_path = os.path.dirname(__file__)

# 程序配置
settings = {
    'debug': %s,
    'gzip': True,
    'cookie_secret' : 'Qcms-by-fms',
    'app_path' : app_path,
    'static_path' : os.path.join(app_path, 'static'),
    'upload_path' : 'file',
    'template_path' : os.path.join(app_path, 'app/view'),
    'autoescape' : None ,
    'run_mode' : '%s' , #行模式有: devel、test 、deploy  三种
    'database' : {
        '%s' : {
            'host' : '%s' ,
            'database' : '%s' ,
            'user' : '%s' ,
            'password' : '%s'
        }
    },
    'session' : {
        'left_time' : 3600 * 24 ,
        'storage' : 'MySql'
    },
    'acl' : acl ,
    'login_url' : '/login',
    'version' : '%s' ,
    'ui_modules' : app.uimodules,
    'port' : %s
}

''' % (
	debug ,
	run_mode ,
	run_mode ,
	host ,
	database ,
	user ,
	password ,
	version ,
	port
)

configFile = open( os.path.join(path , 'config.py') , 'w')
configFile.write(configTpl)
configFile.close()