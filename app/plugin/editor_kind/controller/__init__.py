#coding=utf-8
import app.plugin

class default(app.plugin.Action):
    '''
    插件的前台控制器(无权限控制)
    '''
    def get(self):
        pass

    def post(self):
        pass

class admin(app.plugin.Action):
    '''
    插件的后台控制器
    '''
    def get(self):
        pass

    def post(self):
        pass
    
