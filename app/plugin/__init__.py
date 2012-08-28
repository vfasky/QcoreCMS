#coding=utf-8
import tornado.web
import functools
import app.model as model
import YooYo.util as util
import YooYo.db.mySql
import sys
import YooYo.form

# 存放插件列表
_list = False
# 在工作的插件
_work = False
# 插件的配置
_config = False

# 取插件列表
def getList():
    global _list
    if False == _list:
        reloadList()
    return list

# 重载插件列表
def reloadList():
    global _list
    _list = {}

# 取在工作的插件
def getWork():
    global _work
    if False == _work:
        _work = []
        data = model.Plugin().find().select('name').get(500)
        for v in data:
            _work.append(v['name'])
    return _work

# 取配置
def getConfig(plugin):
    global _config
    if plugin not in getWork() :
        return {}

    if False == _config:
        _config = {}
        data = model.Plugin().find().self('name,config').get(500)
        for v in data:
            _config[v['name']] = util.json.decode(v['config'])

    return _config.get(plugin,{})

# 设置配置
def setConfig(plugin,config):
    global _config
    if plugin not in getWork() :
        return False

    model.Plugin().find('name = ?',plugin).save({
        'config' : util.json.encode(config)
    })

    if _config.get(plugin,False) :
        _config[plugin] = config

# 安装插件
def install(plugin):
    if plugin in getWork() :
        return False
    pluginObj = getInstantiate(plugin)
    if pluginObj:
        desc = pluginObj.__desc__

# 取插件实例
def getInstantiate(plugin):
    try:
        pluginName = 'app.plugin.' + plugin 
        __import__( pluginName )

        if hasattr(sys.modules[pluginName] , plugin):
            return getattr( sys.modules[pluginName] , plugin)()
    except Exception, e:
        return False


class base:
    """插件基类"""

    event = ['beforeExecute','afterExecute','beforeRender']

    def __init__(self):
        self.model = model
        self.mysql = YooYo.db.mySql
        self.form  = YooYo.form
        # 绑定的事件
        self.event = []

    # 表单定义
    def form(self):
        return False

    # 安装时执行
    def onInstall(self):
        return None

    # 卸载时执行
    def onUninstall(self):
        return None

    '''
    绑定事件,支持的事件有:
     - beforeExecute 执行控制器动作之前调用
     - afterExecute 执行控制器动作之后调用
     - beforeRender 渲染之前调用
    ''' 
    def bind(target,event,action):
        if hasattr(self,action) and event in base.event:
            self.event.append({
                'target' : target ,
                'event' : event ,
                'action' : action
            })
        



class UIModule(tornado.web.UIModule):
    '''
    UIModule 插件
    '''
        
    def __init__(self, handler):
        tornado.web.UIModule.__init__(self, handler)

    def static_url(self,url):
        return '/plugin/%s/static/%s' % ( self.__class__.__name__ , url )


class controller:
    '''
    controller 插件
    '''

    # 执行控制器动作之前调用
    @staticmethod
    def beforeExecute(method):

        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            thisAction = self.__class__.__module__ + '.' + self.__class__.__name__
            return method(self, *args, **kwargs)

        return wrapper

    # 执行控制器动作之后调用
    @staticmethod
    def afterExecute(method):

        @functools.wraps(method)
        def wrapper(self, chunk=None):
            thisAction = self.__class__.__module__ + '.' + self.__class__.__name__
            return method(self, chunk)

        return wrapper

    # 渲染之前调用
    @staticmethod
    def beforeRender(method):

        @functools.wraps(method)
        def wrapper(self, template_name, **kwargs):
            thisAction = self.__class__.__module__ + '.' + self.__class__.__name__
            return method(self, template_name, **kwargs)


        return wrapper
