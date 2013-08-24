#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = [
    'AsyncModel',
    'User',
    'Role'
    'UserRole'
] 

from xcat import config
from xcat.mopee import *
from tornado import gen

class AsyncModel(AsyncModel):
    class Meta:
        database = config.get('database')

class User(AsyncModel):
    '''用户表'''
    name = CharField(unique=True, max_length=64)
    password = CharField(max_length=128)
    email = CharField(unique = True)
    sex = IntegerField(default = 0,help_text="0:保密 1:男 2:女")
    register_date = IntegerField()
    
    def gravatar_url(self, size=80):
        return 'http://9429127371.a.uxengine.net/avatar/%s?d=identicon&s=%d' % \
            (md5(self.email.strip().lower()), size)

    @gen.engine
    def get_roles(self, callback=None):
        codes = []
        ids = []
        roles = yield gen.Task(Role.select(Role.id, Role.code)\
                                   .join(UserRole)\
                                   .join(User).where(User.id == self.id)\
                                   .execute)

        for v in roles:
            codes.append(v.code)
            ids.append(v.id)

        if callback:
            callback((codes, ids))

class Role(AsyncModel):
    '''角色表'''

    code = CharField(unique = True, max_length = 64)
    name = CharField()


class UserRole(AsyncModel):
    '''用户角色关联'''

    user = ForeignKeyField(User)
    role = ForeignKeyField(Role) 
        