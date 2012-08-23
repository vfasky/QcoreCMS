#coding=utf-8
import YooYo.mvc.Action
import YooYo.util
import YooYo.db.mySql
import time
import os
import re
import tornado.locale
from tornado import escape
from YooYo.mvc.Action import RequestHandler

class BaseAction(RequestHandler):
    '''
    控制器基类 
    '''

    def initialize(self):
        YooYo.mvc.Action.RequestHandler.initialize(self)
        session = self.get_current_user()
      
        # YooYo.db.mySql.use 别名
        self.db = YooYo.db.mySql.use
        self.user = session


    def set_current_user(self,session):
        self.session['current_user'] = session

    def get_current_user(self):
 
        return self.session['current_user']


    # 没有权限的处理
    def _on_access_denied(self):
        return self.redirect(self.settings['login_url'])

    # 取运行时间
    def get_run_time(self):
        return round(time.time() - self._startTime , 3)

    # 显示提示信息
    def show_msg(self , msg , title=None):
        title = title == None and self._('提示信息') or title
        return self.render('msg.html' , title=title , msg=msg)
        

    def is_mobile(self):
        _mobile = (r'ipod|iphone|android|blackberry|palm|nokia|symbian|'
                   r'samsung|psp|kindle|phone|mobile|ucweb|opera mini|fennec|'
                   r'webos')
        return True if re.search(_mobile, self.user_agent.lower()) else False

    def is_ajax(self):
        return "XMLHttpRequest" == self.request.headers.get("X-Requested-With")

    def write(self, chunk):
        if isinstance(chunk, dict):
            chunk = escape.json_encode(chunk)
            callback = self.get_argument('callback', None)
            if callback:
                chunk = "%s(%s)" % (callback, escape.to_unicode(chunk))
                self.set_header("Content-Type",
                                "application/javascript; charset=UTF-8")
            else:
                self.set_header("Content-Type",
                                "application/json; charset=UTF-8")

        if True == self.settings['is_dev'] : self.set_header("RUN-TIME", str(self.get_run_time()))
        super(RequestHandler, self).write(chunk)



