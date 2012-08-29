#coding=utf-8
import tornado.web
import functools
import app.model as model
import YooYo.util as util
import YooYo.db.mySql
import sys
import os
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
        '''
        结构:
        _list = {
            'event' : {
                'controller' : [
                    {'plugin' , 'action'},
                    ...
                ]
            } ,
            ...
        '''
        _list = {
            'beforeExecute' : {} ,
            'afterExecute' : {} ,
            'beforeRender' : {} ,
        }
        data = model.Plugin().find().select('name,bind').get(500)
        
        for v in data:
            'target event action'
            binds = util.json.decode(v['bind'])
    
            for bind in binds:

                eventList = _list[bind['event']]
                if False == eventList.get(bind['target'] , False) :
                    eventList[bind['target']] = []

                eventList[bind['target']].append({
                    'plugin' : v['name'] ,
                    'action' : bind['action']
                })

                _list[bind['event']] = eventList


    return _list

# 重载插件缓存
def reload():
    global _list
    global _work
    global _config
    _list = False
    _work = False
    _config = False

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
        name = plugin
        config = '{}'

        pluginObj.onInstall()

        if pluginObj.form() :
            config = pluginObj.form().getDefaultValues()

        bind = pluginObj._bind
        id = model.Plugin().find().add({
            'name' : name ,
            'config' : util.json.encode(config) ,
            'bind' : util.json.encode(bind)
        })
        if id :
            reload()
            return True

    return False

# 卸载插件
def uninstall(plugin):
    if plugin not in getWork() :
        return False
    pluginObj = getInstantiate(plugin)
    if pluginObj:
        pluginObj.onUninstall()
        model.Plugin().find('name = ?' , plugin).delete()
        reload()
        return True
    return False

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

    event = ('beforeExecute','afterExecute','beforeRender')

    def __init__(self):
        self._model = model
        self._mysql = YooYo.db.mySql
        self._form  = YooYo.form
        # 绑定的事件
        self._bind = []
        # 上下文
        self._context = {}

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
    def bind(self,target,event,action):
        if hasattr(self,action) and event in base.event:
            self._bind.append({
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
       
            eventList = getList()['beforeExecute']
            thatPlugins = eventList.get(thisAction,False)
            if thatPlugins:

                for info in thatPlugins:
                    pluginObj = getInstantiate(info['plugin'])
                    # 执行插件
                    if pluginObj:
                        pluginObj._context['args'] = args
                        pluginObj._context['self'] = self
                        pluginObj._context['kwargs'] = kwargs
                      

                        if False == getattr(pluginObj,info['action'])():
                        
                            return False

                        self = pluginObj._context['self']
                        args = pluginObj._context['args'] 
                        kwargs = pluginObj._context['kwargs']    

            return method(self, *args, **kwargs)

        return wrapper

    # 执行控制器动作之后调用
    @staticmethod
    def afterExecute(method):

        @functools.wraps(method)
        def wrapper(self, chunk=None):
            thisAction = self.__class__.__module__ + '.' + self.__class__.__name__
            
            eventList = getList()['afterExecute']
            thatPlugins = eventList.get(thisAction,False)
            if thatPlugins:
                for info in thatPlugins:
                    pluginObj = getInstantiate(info['plugin'])
                    # 执行插件
                    if pluginObj:
                
                        pluginObj._context['self'] = self
                        pluginObj._context['chunk'] = chunk
                 
                        if False == getattr(pluginObj,info['action'])():
                        
                            return False

                        self = pluginObj._context['self']
                        chunk = pluginObj._context['chunk']
                  
            return method(self, chunk)

        return wrapper

    # 渲染之前调用
    @staticmethod
    def beforeRender(method):

        @functools.wraps(method)
        def wrapper(self, template_name, **kwargs):
            thisAction = self.__class__.__module__ + '.' + self.__class__.__name__
            
            eventList = getList()['beforeRender']
            thatPlugins = eventList.get(thisAction,False)
            if thatPlugins:
                for info in thatPlugins:
                    pluginObj = getInstantiate(info['plugin'])
                    # 执行插件
                    if pluginObj:
                
                        pluginObj._context['self'] = self
                        pluginObj._context['template_name'] = template_name
                        pluginObj._context['kwargs'] = kwargs

                        if False == getattr(pluginObj,info['action'])():
                       
                            return False

                        self = pluginObj._context['self']
                        template_name = pluginObj._context['template_name']
                        kwargs = pluginObj._context['kwargs']

            return method(self, template_name, **kwargs)


        return wrapper

class Action:
    '''
    插件的控制器
    '''
    def __init__(self, host , plugin) :
        self._host = host
        self._plugin = plugin

    def write(self, chunk):
        return self._host.write(chunk)

    def static_url(self, path):
        return '/plugin/%s/static/%s' % ( self._plugin , path )

    def render(self, template_name, **kwargs):
        template_name = 'app/plugin/%s/view/%s' % ( self._plugin , template_name )
        template_name = os.path.join( self._host.settings['app_path'] , template_name)
        return self._host.render(template_name,**kwargs)

