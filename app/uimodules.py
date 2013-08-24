#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2013-08-24 16:23:58
# @Author  : vfasky (vfasky@gmail.com)
# @Link    : http://vfasky.com
# @Version : $Id$
import math
import urllib
from copy import deepcopy
from tornado.web import UIModule
from xcat.web import route

class Pagination(UIModule):
    '''分页条'''

    def build_left(self):
        if self.count_page < self.max:
            return range(1,self.count_page + 1) 

        c_max = int( math.ceil( self.max / 2 ) )

        if self.current_page <= c_max:
            return range(1,c_max) 

        return range(self.current_page - c_max, self.current_page) 
       
    def build_right(self): 
        if self.count_page < self.max : return [] 

        c_max = int( math.ceil( self.max / 2 ) )
        if self.current_page <= c_max:
            return range(c_max,self.max + 1) 

        if self.current_page + c_max > self.count_page:
            return range(self.current_page, self.count_page + 1)
            
        return range(self.current_page, self.current_page + c_max)
      
    def build_url(self,page_num):
        url_args = deepcopy(self.url_args)
        
        if '_page_' in self.args:
            self.args[ self.args.index('_page_') ] = page_num
        else:
            url_args.append('page=%s' % page_num)
     

        url = route.url_for(self.route_name, *self.args)

        if len(url_args) > 0:
            url = url + '?' + '&'.join(url_args)

        return url



    def render(self,count = 0,current_page = 1,
               args=[], kw={},
               page_size=10,route_name=None,
               view_name=None,max_item=10):
        self.route_name   = route_name or self.handler.routes[0].get('name') 
        self.view_name    = view_name or 'ui/_pagination.html' 
        self.count_page   = int(math.ceil( float(count) / float(page_size) ))
        
        if self.count_page < 2: return ''

        self.current_page = int(current_page)
        self.max          = int(max_item)
        if self.current_page > self.count_page:
            self.current_page = self.count_page
        
        self.next_page = self.current_page + 1
        if self.next_page >= self.count_page:
            self.next_page = self.count_page

        self.prev_page = self.current_page - 1
        if self.prev_page < 1:
            self.prev_page = 1

        url_args = []
        for k in kw:
            url_args.append('%s=%s' % (k, urllib.quote(kw[k]) ) )

        self.url_args = url_args
        self.args     = args

        page_list = self.build_left() + self.build_right()
        page_urls = []
        for v in page_list:
            page_urls.append({
                'num' : v ,
                'url' : self.build_url(v)
            })

        return self.render_string(self.view_name,
            page_urls    = page_urls ,
            page_size    = page_size ,
            count_page   = self.count_page ,
            count        = count ,
            next_page    = self.build_url(self.next_page) ,
            prev_page    = self.build_url(self.prev_page) ,
            current_page = self.current_page 
        )