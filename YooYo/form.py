#coding=utf-8
import YooYo.util
from tornado import escape

class validators:
    """表单验证类"""

    @staticmethod
    def isJson(json):
   
        if json is None :
            return {
                'success' : True
            }
        try:
            escape.json_decode(json)
            return {
                'success' : True
            }
        except Exception, e:
            return {
                'success' : False ,
                'msg' : 'JSON格式错误'
            }


    @staticmethod
    def isEmail(str):
        if YooYo.util.validators.isEmail(str):
            return {
                'success' : True
            }
        return {
            'success' : False ,
            'msg' : '邮箱格式错误'
        }

    @staticmethod
    def isNumber(str):
        if YooYo.util.validators.isNumber(str):
            return {
                'success' : True
            }
        return {
            'success' : False ,
            'msg' : '只能为数字'
        }

    @staticmethod
    def notEmpty(str):
        if False == YooYo.util.validators.isEmpty(str):
            return {
                'success' : True
            }
        return {
            'success' : False ,
            'msg' : '不能为空'
        }


class filters(YooYo.util.filters):
    """过滤"""
    

class FormElementBase:
    """表单 element 基类"""
    def __init__(self, **arg):

        self._name  = arg['name']
        self._label = arg.has_key('label') and arg['label'] or arg['name']
        self._value = arg.has_key('value') and arg['value'] or None
        self._attr  = arg.has_key('attr') and arg['attr'] or {}
        self._validators = arg.has_key('validators') and arg['validators'] or []
        self._filters = arg.has_key('filters') and arg['filters'] or []
        self._data  = arg.has_key('data') and arg['data'] or []
        self._type  = 'text'
        self._on      = {
            # 验证错误时, 回调
            'validateError' : FormElementBase.onValidateError
        }
        
    @staticmethod
    def onValidateError(element , msg):
        return element.label() + ' : ' + msg

    # 返回 label
    def label(self):
        return self._label

    # 事件绑定
    def on(self,event,callback):
        self._on[event] = callback

    # 设置值
    def setValue(self,value):
        
        if YooYo.util.validators.isArray(value) and len(value) == 1:
            value = value[0]

        if YooYo.util.validators.isNumber(value):
            value = int(value)

        if len(self._data) == 0:
            #过滤
            for v in self._filters:
                if hasattr(filters , v):
                    value = getattr(filters , v)(value)

            self._value = value

            return 

        for v in self._data :
            
            
            if str(v['value']) == str(value) :
                self._value = v['value']
                return


    # 取值
    def getValue(self):

        return self._value

    # 取配置
    def getConfig(self):
        return {
            'name' : self._name ,
            'label' : self._label ,
            'value' : self._value ,
            'attr' : self._attr ,
            'validators' : self._validators ,
            'filters' : self._filters ,
            'data' : self._data ,
            'type' : self._type 
        }

    # 验证数据
    def validate(self):
        value = self.getValue()

        for v in self._validators:
            if hasattr(validators , v):
                ret = getattr(validators , v)(value)
                #print ret
                if False == ret['success']:
                    self._on['validateError'](self , ret['msg'])
                    return False
        return True

class Button(FormElementBase):
    
    def __init__(self, **arg):
        FormElementBase.__init__(self, **arg)
        self._type = 'button'

    def setValue(self,value):
        self._value = value

    def validate(self):
        return True
        
class Submit(FormElementBase):
    def __init__(self, **arg):
        FormElementBase.__init__(self, **arg)
        self._type = 'submit'

    def setValue(self,value):
        self._value = value

    def validate(self):
        return True


class Hidden(FormElementBase):
    def __init__(self, **arg):
        FormElementBase.__init__(self, **arg)
        self._type = 'hidden'
        

class Password(FormElementBase):
    def __init__(self, **arg):
        FormElementBase.__init__(self, **arg)
        self._type = 'password'
        

class Text(FormElementBase):
    def __init__(self, **arg):
        FormElementBase.__init__(self, **arg)
        self._type = 'text'

class Photos(FormElementBase):
    def __init__(self, **arg):
        FormElementBase.__init__(self, **arg)
        self._type = 'photos'

class ImageUpload(FormElementBase):
    def __init__(self, **arg):
        FormElementBase.__init__(self, **arg)
        self._type = 'imageUpload'
        

class Select(FormElementBase):
    def __init__(self, **arg):
        FormElementBase.__init__(self, **arg)
        self._type = 'select'
        

class Radio(FormElementBase):
    def __init__(self, **arg):
        FormElementBase.__init__(self, **arg)
        self._type = 'radio'

class Textarea(FormElementBase):
    def __init__(self, **arg):
        FormElementBase.__init__(self, **arg)
        self._type = 'textarea'

class Editor(FormElementBase):
    def __init__(self, **arg):
        FormElementBase.__init__(self, **arg)
        self._type = 'editor'

class Videos(FormElementBase):
    def __init__(self, **arg):
        FormElementBase.__init__(self, **arg)
        self._type = 'videos'

class Checkbox(FormElementBase):
    def __init__(self, **arg):
        FormElementBase.__init__(self, **arg)
        self._type = 'checkbox'
        self._value = []

    # 设置值
    def setValue(self,value):
        self._value = []
        for v in self._data :
            for v1 in value: 
                if str(v['value']) == str(v1) :
                    self._value.append(v['value'])

    # 取值
    def getValue(self):

        return self._value

class Form:
    '''
    表单对象 Form
    ======================

    ### python:

        from YooYo.form import Form
        from YooYo.form import Text
        from YooYo.form import Password

        # 验证错误是回调
        def onFormValidateError(element,msg):
            return self.write(element.label() + ':' + msg)

        # 添加自定义验证
        def formValidatorTest(value):
            return {
                'success' : False ,
                'msg' : '我说你错'
            }

        # 添加自定义过滤
        def formFilterTest(value):
            return test + value

        # 定义表单对象
        form = Form()
        # 绑定自定义验证
        form.addValidator('test' , formValidatorTest)
        # 绑定自定义过滤
        form.addFilter('test' , formFilterTest)

        # 构造元素
        form.add(Text(
            name = 'test' ,
            label = '测试' ,
            validators = [ 'test' ,'isNumber']
        )).add(Password(
            name = 'empty' ,
            label = '空标题' ,
            validators = ['notEmpty'] ,
            filter = ['test']
        ))
        
        # 绑定错误回调
        form.on('validateError' , self.onFormValidateError)

        # 验证
        if form.validate(self.request.arguments) :
            # 验证通过
            print form.values()

    '''
    def __init__(self, action="" , method="POST" , enctype="multipart/form-data" , attr=[]):
        self.action    = action
        self.method    = method
        self.enctype   = enctype
        self.attr      = attr
        self._elements = []
        self._values   = {}
        self._on = {
            # 验证错误时, 回调
            'validateError' : FormElementBase.onValidateError
        }

    # 事件绑定
    def on(self,event,callback):
        self._on[event] = callback
        for e in self._elements:
            e.on(event,callback)

    # 添加验证
    def addValidator(self,name,callback):
        setattr(validators , name , callback)

    # 添加过滤
    def addFilter(self,name,callback):
        setattr(filters , name , callback)

    # 添加元素
    def add(self,element):
        element.on('validateError',self._on['validateError'])
        self._elements.append(element)
        return self

    def getConfig(self):
        config = {
            'action' : self.action ,
            'method' : self.method ,
            'enctype' : self.enctype ,
            'attr' : self.attr ,
            'elements' : [] ,
        }
        for e in self._elements:
            config['elements'].append(e.getConfig())

        return config

    # 取验证过后的数据
    def values(self):
        return self._values

    # 设置表单值
    def setValues(self,data):
        for e in self._elements:
            if data.has_key(e._name):
                e.setValue(data[e._name])
            elif YooYo.util.validators.isNumber(e._name) and data.has_key(int(e._name)):
                e.setValue(data[int(e._name)])

    # 取表单默认值(注:值未经过验证)
    def getDefaultValues(self):
        values = {}
        for e in self._elements: 
            values[e._name] = e.getValue()
        return values

    # 验证数据
    def validate(self,data):
        _data = {}
        for k in data:
            _data[ k.replace('[]' , '') ] = data[k]

        for e in self._elements:       
            if _data.has_key(e._name):
                e.setValue(_data[e._name])
            elif YooYo.util.validators.isNumber(e._name) and _data.has_key(int(e._name)):
                e.setValue(_data[int(e._name)])

            if e.validate():
                if e._type != 'submit' and e._type != 'button':
                    self._values[e._name] = e.getValue()
            else:
                return False
        return True
        