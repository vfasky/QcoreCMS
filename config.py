#coding=utf-8
import os

# 控制器
import app.controller.default
import app.controller.admin

# ui_modules
import app.uimodules

# 路由
routes = [
    (r"/", app.controller.default.index),
    (r"/PIE.htc", app.controller.default.PIE),
    (r"/plugin/(\w+)/static/([a-zA-Z_./-0-9]+)$", app.controller.default.pluginStatic),

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
    (r"/admin/plugin", app.controller.admin.plugin),

    (r"/admin/model", app.controller.admin.models),
    (r"/admin/model-field-(\d+)$", app.controller.admin.model_field),

    (r"/admin/category", app.controller.admin.category),

    (r"/admin/uploadFile", app.controller.admin.uploadFile),
    
    (r"/(.+)$", app.controller.default._404),
]

'''
访问规则
=================

特殊标识: 

 - ACL_NO_ROLE 没有角色用户
 - ACL_HAS_ROLE 有角色用户
 
'''
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
    'app.controller.admin.plugin' : {
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
    'debug': True,
    'gzip': True,
    'cookie_secret' : 'Qcms-by-fms',
    #'xsrf_cookies' : True,
    'app_path' : app_path,
    'static_path' : os.path.join(app_path, 'static'),
    'upload_path' : 'file',
    'template_path' : os.path.join(app_path, 'app/view'),
    'autoescape' : None ,
    'run_mode' : 'devel' , #行模式有: devel、test 、deploy  三种
    'database' : {
        'devel' : {
            'host' : '127.0.0.1:3306' ,
            'database' : 'qcms' ,
            'user' : 'root' ,
            'password' : ''
        },
        'deploy' : {
            'host' : '127.0.0.1:3306' ,
            'database' : 'qcms' ,
            'user' : 'root' ,
            'password' : ''
        }
    },
    'session' : {
        'left_time' : 3600 * 24 ,
        'storage' : 'MySql'
    },
    'acl' : acl ,
    'login_url' : '/login',
    'version' : '1.0.0-dev' ,
    'ui_modules' : app.uimodules,
    'port' : 8889
}
