#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = [
    'Login',
]

import arrow
from xcat.form import Form, validators, fields
from tornado import gen

class Login(Form):
    '''登陆表单'''
    email = fields.TextField(
        'Email', [
            validators.Required(),
            validators.Length(min=4, max=30),
            validators.Email(),
        ]
    )
    password = fields.PasswordField(
        'Password',[
            validators.Required(),
        ]
    )