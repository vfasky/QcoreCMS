#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2013-08-24 16:23:58
# @Author  : vfasky (vfasky@gmail.com)
# @Link    : http://vfasky.com
# @Version : $Id$
__all__ = [
    'Index',
    'Login',
]
import time

from xcat.web import RequestHandler, route, form, session
from xcat.utils import sha1
from tornado import gen
from tornado.web import asynchronous
from app.models import User
from tornado.util import import_object


@route(r"/admin", allow=['admin'])
class Index(RequestHandler):

    '''Admin Cp'''

    def get(self):
        #print self.current_user
        self.render('admin/index.html')

@route(r"/admin/form", allow=['admin'])
class Form(RequestHandler):

    '''取表单的html结构'''
    @asynchronous
    @gen.engine
    def get(self):
        form_name = self.get_argument('form')
        if not form_name:
            self.finish()
            return

        locale_code = 'en_US'
        if hasattr(self, 'locale') and hasattr(self.locale, 'code'):
            locale_code = self.locale.code

        try:
            form_obj = import_object(form_name)(locale_code=locale_code)
        except Exception:
            self.finish()
            return
        
        form_obj.xsrf_form_html = self.xsrf_form_html
        yield gen.Task(form_obj.load_field_data)
        form_obj.load_data(self.request.arguments)

        self.render('admin/form.html', form=form_obj)
        


@route(r"/admin/login")
class Login(RequestHandler):

    '''Admin Login'''

    @form('app.forms.Login')
    def get(self):
        self.render('admin/login.html', form=self.form)

    @form('app.forms.Login')
    @session
    @gen.engine
    @asynchronous
    def post(self):
        if not self.form.validate():
            self.render('admin/login.html',
                        form=self.form
                        )
            return
        # 防止穷举
        time.sleep(1.5)

        post = self.form.data
        user = User.select().where(User.email == post['email'])\
                            .where(User.password == sha1(post['password']))

        if 0 == (yield gen.Task(user.count)):
            self.form.email.errors.append('Email 或 密码错误')
            self.render('admin/login.html',
                        form=self.form
                        )
            return

        user = yield gen.Task(user.get)
        role_codes, role_ids = yield gen.Task(user.get_roles)

        # 写入 session
        self.set_current_user({
            'id': user.id,
            'gravatar': user.gravatar_url(80),
            'name': user.name,
            'email': user.email,
            'sex': user.sex,
            'roles': role_codes
        })

        self.redirect(route.url_for('admin.Index'))
