#!/usr/bin/env python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Version : $Id$

__all__ = [
    'settings',
]

import os
from xcat import mopee

# app所在目录
app_path = os.path.dirname(__file__)

settings = {
    'site_name': 'QcoreCMS',  # 网站名
    'admin_name': 'admin',  # 安装时的管理员用户名
    'admin_email': 'admin@admin.com',  # 管理员邮箱
    'admin_passwd': 'XcatCMS2',  # 安装时的管理员密码
    'debug': True,
    'xsrf_cookies': True,
    'cookie_secret': 'QcoreCMS-Xcat-app',
    'app_path': app_path,
    'static_path': os.path.join(app_path, 'static'),
    'template_path': os.path.join(app_path, 'app', 'views'),
    'locale_path': os.path.join(app_path, 'locale'),
    'run_mode': 'devel',  # 运行模式有: devel、deploy
    'version': '2.0.0-dev',
    'devel': {
        'database': mopee.PostgresqlAsyncDatabase('qcorecms',
                                                  user='',
                                                  host='127.0.0.1',
                                                  password='',
                                                  size=40,
                                                  ),
        'session': {
            'storage': 'Memcache',
            'config': {
                'servers': ['127.0.0.1:11211'],
                'left_time': 3600 * 24,
                'maxclients': 100,
            }
        },
        'cache': {
            'storage': 'Memcache',
            'config': {
                'servers': ['127.0.0.1:11211'],
                'maxclients': 100,
            }
        },
    },
    'deploy': {
        'database': mopee.PostgresqlAsyncDatabase('qcorecms',
                                                  user='',
                                                  host='127.0.0.1',
                                                  password='',
                                                  size=40,
                                                  ),
        'session': {
            'storage': 'Memcache',
            'config': {
                'servers': ['127.0.0.1:11211'],
                'left_time': 3600 * 24,
                'maxclients': 300,
            }
        },
        'cache': {
            'storage': 'Memcache',
            'config': {
                'servers': ['127.0.0.1:11211'],
                'maxclients': 300,
            }
        },
    },
}
