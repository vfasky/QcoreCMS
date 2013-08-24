#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2013-08-24 16:23:58
# @Author  : vfasky (vfasky@gmail.com)
# @Link    : http://vfasky.com
# @Version : $Id$

import os
import glob

path     = os.path.dirname(__file__)
handlers = []

for name in os.listdir(path):
    if os.path.isdir(os.path.join(path,name)) :
        handlers.append(name)

__all__ = handlers