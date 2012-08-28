#coding=utf-8
import os
import YooYo.util as util
class UIModule:
    """ui model 的扩展"""

    basePath = os.path.join( os.path.dirname(__file__) , 'ui' )

    def __init__(self,model,*args, **kwargs):
        self._css = []
        self._js = []
        self._cssFile = []
        self._jsFile = []
        self._head = []
        self._body = []
        self._bind = []
        self._model = model
        self._args = args
        self._kwargs = kwargs

    # 添加css
    def addCss(self,string):
        self._css.append(string)
        return self

    # 添加css文件
    def addCssFile(self,path):
        self._cssFile.append(path)
        return self

    # 添加js
    def addJs(self,string):
        self._js.append(string)
        return self

    # 添加js文件
    def addJsFile(self,path):
        self._jsFile.append(path)
        return self

    # 在 head 插入代码
    def addHead(self,string):
        self._head.append(string)
        return self

    # 在 body 插入代码
    def addBody(self,string):
        self._body.append(string)
        return self

    def htmlHead(self):
        head = ''.join(self._head)

        if len(self._css) > 0 :
            head = head + '<style type="text/css">%s</style>' % ''.join(self._css) 
 
        css = []
        for link in self._cssFile :
            css.append('<link href="%s" rel="stylesheet" type="text/css" media="screen" />' % link)

        head = head + ''.join(css)

        js = []
        for path in self._jsFile:
            js.append('<script src="%s" type="text/javascript"></script>' % path)


        head = head + ''.join(js)

        return head


    def htmlBody(self):
        body = ''.join(self._body)

        if len(self._js) > 0 :
            body = body + '<script type="text/javascript">%s</script>' % "\r\n".join(self._js)

        return body

    # 执行
    def execute(self,action,html=False):
        if hasattr(self,action):
            if False != html:
                return getattr(self,action)(html)

            ret = getattr(self,action)()
            if False == ret :
                return False

            return {
                'self' : self._model ,
                'args' : self._args ,
                'kwargs' : self._kwargs
            }

    
    # 绑定 UIModel
    def bind(self,name,action,event='before'):
        self._bind.append({
            'name' : name ,
            'event' : event ,
            'action' : action ,
            'plugin' : self.__class__.__name__
        })
        return self
        