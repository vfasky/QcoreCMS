#coding=utf-8
from app.controller import BaseAction

import YooYo
import YooYo.form 
import YooYo.util as util
import app.model as model
import app.plugin
import os 
import sys

class Action(BaseAction):
    @app.plugin.controller.beforeRender
    def render(self, template_name, **kwargs):
        super(BaseAction, self).render(template_name, **kwargs)

    @app.plugin.controller.afterExecute
    def finish(self, chunk=None):
        super(BaseAction, self).finish(chunk)


class index(Action):
    @app.plugin.controller.beforeExecute
    @YooYo.acl
    def get(self):

        self.render('admin/index.html')

class logout(Action):
    @app.plugin.controller.beforeExecute
    @YooYo.acl
    def get(self):
        self.session.clear()
        self.redirect('/login')
        

class login(Action):

    def form(self):
        form = YooYo.form.Form()
        form.add(YooYo.form.Text(
            name = 'email',
            label = '邮箱',
            validators = ['notEmpty','isEmail'] ,
            filter = ['trim']
        )).add(YooYo.form.Password(
            name = 'password',
            label = '密码',
            filter = ['trim'] ,
            validators = ['notEmpty'] ,
        )).add(YooYo.form.Submit(
            name = 'send' ,
            label = '登陆' 
        ))
        return form

    @app.plugin.controller.beforeExecute
    def get(self):
        self.render('admin/login.html',form=self.form().getConfig())

    @app.plugin.controller.beforeExecute
    def post(self):
        import time
        time.sleep(1.5)

        form = self.form()

        # 验证
        if form.validate(self.request.arguments):
            # 验证通过
            post = form.values()
            ar = model.User().find('email = ?' , post['email'])\
                             .where('password = ?' , util.md5(post['password']))

            user = ar.get()
            if user != None:
                # 为用户登陆
                self.set_current_user({
                    'userId' : user['id'],
                    'userName' : user['name'],
                    'email' : user['email'] ,
                    'roles' : user.getRoleCodes() , 
                })
             
                return self.write({'success' : True , 'url' : '/admin'});


        return self.write({'success' : False , 'msg' : '邮箱或密码错误'})

class pluginController(Action):
    """插件的后台 controller 钩子"""

    def getInstantiate(self,plugin):
        if plugin in app.plugin.getWork():
            try:
                controller = 'app.plugin.' + plugin + '.controller'   
                __import__( controller )

                if hasattr(sys.modules[controller] , 'admin'):
                    return getattr(sys.modules[controller] , 'admin')(self,plugin)
            except Exception, e:
                return False
        return False

    @YooYo.acl
    def get(self,plugin):
        controller = self.getInstantiate(plugin)
     
        if controller :
            return controller.get()

    @YooYo.acl
    def post(self,plugin):
        controller = self.getInstantiate(plugin)
        if controller :
            return controller.post()

class plugin(Action):
    '''插件管理'''

    # 取插件列表
    def getPlugins(self):
        path = os.path.join(self.settings['app_path'] , 'app/plugin')
        init = str( os.path.join( path , '__init__.py') )
        key  = init.split( '__init__.py' )

        import glob
        list = glob.glob( os.path.join( path , '*.py') )

        plugins = []
        for name in list:
            name = str(name)
            if init != name:
                plugins.append( name.replace( key[0] , '' ).replace('.py' , '') )

        for name in os.listdir(path):
            if os.path.isdir( os.path.join(path,name) ) :
                plugins.append(name)
        return plugins

    @app.plugin.controller.beforeExecute
    @YooYo.acl
    def get(self):

        # 已激活的插件
        wordList = app.plugin.getWork()
        # 所有插件列表
        allList = self.getPlugins()
        # 可用插件
        pluginList = []
        for p in allList:
            if p not in wordList:
                pluginList.append(p)

        words = []
        for w in wordList:
            pluginObj = app.plugin.getInstantiate(w)
            words.append({
                'name' : w ,
                'form' : pluginObj.form() and True or False,
                'info' : pluginObj.__class__.__doc__
            })

        plugins = []
        for p in pluginList:

            plugins.append({
                'name' : p ,
                'info' : app.plugin.getInstantiate(p).__class__.__doc__
            })

        self.render('admin/plgin.html',
                    plugins=plugins,
                    words=words)

    @app.plugin.controller.beforeExecute
    @YooYo.acl
    def post(self):
        if self.get_argument('act') == 'activation' :
            plugin = self.get_argument('name')
            if app.plugin.install(plugin):
                return self.write({
                    'success' : True 
                })
            else:
                return self.write({
                    'success' : False ,
                    'msg' : '插件不存在 或 已经激活!'
                })

        if self.get_argument('act') == 'disable' :
            plugin = self.get_argument('name')
            if app.plugin.uninstall(plugin):
                return self.write({
                    'success' : True 
                })
            else:
                return self.write({
                    'success' : False ,
                    'msg' : '插件禁用失败!'
                })




class uploadFile(Action):
    """上传文件"""

    @app.plugin.controller.beforeExecute
    @YooYo.acl
    def get(self):
        return

    @app.plugin.controller.beforeExecute
    @YooYo.acl
    def post(self):
        if not self.request.files.has_key('fileData'):
            return self.write({ 'error': 1 , 'message' : '没有文件被上传' })

        path = '/' + self.settings['upload_path'] + '/' + util.date.timeToStr('%Y-%m') + '/' 
        if False == os.path.exists(self.settings['static_path'] + path):
            os.mkdir(self.settings['static_path'] + path)

        fileData = self.request.files['fileData'][0]
        nameInfo = fileData['filename'].split('.')
        suffix = nameInfo[ len(nameInfo) - 1 ]


        fileName = util.md5(fileData['filename'] + str(util.time.time())) + '.' + util.filters.trim(suffix)
        filePath = self.settings['static_path'] + path + fileName
        fileHandle = open(filePath , 'wb')
        fileHandle.write(fileData['body'])
        fileHandle.close()

        url = '/static' + path + fileName
        model.Attachment().add({
            'ip' : self.request.remote_ip ,
            'url' : url ,
            'user_id' : self.user['userId'] ,
            'title' : fileData['filename'] ,
            'type' : fileData['content_type'] ,
            'size' : os.path.getsize(filePath) / 1024
        })

        return self.write({ 
            'error': 0 , 
            'suffix' : suffix ,
            'fileName' : fileData['filename'] ,
            'type' : fileData['content_type'],
            'url' : url 
        })

class contentEdit(Action):
    '''编辑内容'''

    def form(self,id):

        form = model.Model().getForm(id)
        return form.add(YooYo.form.Submit(
            name = 'send' ,
            label = '保存' 
        ))

    @app.plugin.controller.beforeExecute
    @YooYo.acl
    def get(self,id,aid,cid):
        category = model.Category().get(id)
        if category :
            locales = model.Locale().find().get(100)
            form = self.form(category['model_id'])
            ar = model.Category().getModel(id)
            data = ar.where('category_has_article_id = ?' , cid).get(100)

            self.render('admin/content_save.html',
                        locales=locales,
                        category=category,
                        data=data,
                        editor='editor_base',
                        aid=aid,
                        form=form.getConfig())

    @app.plugin.controller.beforeExecute
    @YooYo.acl
    def post(self,id,aid,cid):
        category = model.Category().get(id)
        if category :
            form = self.form(category['model_id'])
            data = util.json.decode(self.get_argument('list' , '[]') , [])

            for post in data :
                # print post

                # 验证
                if form.validate(post):
                    ar = model.Category().getModel(id)
                    # 验证通过
                    post = form.values()

                    if util.validators.isNumber(post['id']) :
                        post['category_has_article_id'] = cid
                        post['user_id'] = self.user['userId']
                        post['change_time'] = util.time.time()
                        post['ip'] = self.request.remote_ip
                        ar.where('id = ?' , post['id']).save(post)
                    else:
                        del post['id']
                        post['category_has_article_id'] = cid
                        post['user_id'] = self.user['userId']
                        post['time'] = util.time.time()
                        post['change_time'] = 0
                        post['ip'] = self.request.remote_ip
                        ar.add(post)


            return self.write({'success' : True})
        return self.write({'success' : False , 'msg' : '数据异常'})

        

class contentAdd(Action):
    '''添加内容'''

    def form(self,id):

        form = model.Model().getForm(id)
        return form.add(YooYo.form.Submit(
            name = 'send' ,
            label = '添加' 
        ))

    @app.plugin.controller.beforeExecute
    @YooYo.acl
    def get(self,id):

        category = model.Category().get(id)
        if category :
            locales = model.Locale().find().get(100)
            form = self.form(category['model_id'])
            self.render('admin/content_save.html',
                        locales=locales,
                        category=category,
                        editor='editor_base',
                        aid=False,
                        form=form.getConfig())

    @app.plugin.controller.beforeExecute
    @YooYo.acl
    def post(self,id):
        category = model.Category().get(id)
        if category :
            form = self.form(category['model_id'])
            data = util.json.decode(self.get_argument('list' , '[]') , [])

            # 创建关联
            cid = model.CategoryHasArticle().find().add({
                'category_id' : id ,
            })
            
            for post in data :
                # print post

                # 验证
                if form.validate(post):
                    ar = model.Category().getModel(id)
                    # 验证通过
                    post = form.values()
                    del post['id']
                    post['category_has_article_id'] = cid
                    post['user_id'] = self.user['userId']
                    post['time'] = util.time.time()
                    post['change_time'] = 0
                    post['ip'] = self.request.remote_ip
                    ar.add(post)

            return self.write({'success' : True})
        return self.write({'success' : False , 'msg' : '数据异常'})

class contentList(Action):
    '''内容列表'''

    @app.plugin.controller.beforeExecute
    @YooYo.acl
    def get(self,id):
        ar = model.Category().getModel(id)
        
        if ar:
            ar.join('qc_category_has_article AS C ON C.id = %s.category_has_article_id' % ar._from)\
              .join('qc_locale AS L ON L.id = %s.locale_id' % ar._from)\
              .order('C.id DESC')\
              .select('%s.id,%s.title,C.id AS cid,L.name' % (ar._from,ar._from))\
              .where('C.category_id = ?',id)\
              .page(self.get_argument('page',1),10)

            if self.get_argument('q',False) :
                ar.where('%s.title LIKE ?' % ar._from , '%'+self.get_argument('q')+'%')

        
            data = ar.query()
        else:
            data = []

        self.render('admin/content_list.html',
                    id=id,
                    saerch=self.get_argument('q',''),
                    pagination=ar.getPagination(),
                    data=data)


    # 删除文章
    @app.plugin.controller.beforeExecute
    @YooYo.acl
    def post(self,id):
        ar = model.Category().getModel(id)
        
        if ar and self.get_argument('id',False):
            ar.where('id = ?' , self.get_argument('id')).delete()
            return self.write({'success' : True})
        return self.write({'success' : False ,'msg' : '参数异常'})

        

class content(Action):
    '''内容管理'''

    @app.plugin.controller.beforeExecute
    @YooYo.acl
    def get(self):
        categoryAr = model.Category()
        category = categoryAr.treeToSelect()

        self.render('admin/content.html',category=category)
        

class user(Action):
    '''会员管理'''

    def form(self):
        roles = []
        for r in model.Role().find().get(20):
            roles.append({
                'label' : r['info'] ,
                'value' : r['id']
            })

        form = YooYo.form.Form()
        form.add(YooYo.form.Hidden(
            name = 'id' 
        )).add(YooYo.form.Text(
            name = 'name',
            label = '账号',
            validators = ['notEmpty'] ,
            filter = ['trim']
        )).add(YooYo.form.Password(
            name = 'password',
            label = '密码',
            filter = ['trim'] ,
            attr = {
                'tip' : '不修改请留空'
            }
        )).add(YooYo.form.Text(
            name = 'email',
            label = '邮箱',
            validators = ['notEmpty','isEmail'] ,
            filter = ['trim']
        )).add(YooYo.form.Checkbox(
            name = 'roles',
            label = '角色',
            data = roles
        )).add(YooYo.form.Submit(
            name = 'send' ,
            label = '保存' 
        ))
        return form

    @app.plugin.controller.beforeExecute
    @YooYo.acl
    def get(self):
        ar = model.User().find()\
                         .order('id DESC')\
                         .page(self.get_argument('page',1) , 10)

        data  = []
        for v in ar.query():
            user = v.attr
            roles = []
            user['data']= { 'roles' : v.getRoles() }
            for r in user['data']['roles']:
                roles.append(r['info'])
            user['roles'] = ','.join(roles)
            data.append(user)

        self.render('admin/user.html',
                    data=data,
                    form=self.form().getConfig(),
                    pagination=ar.getPagination())

    @app.plugin.controller.beforeExecute
    @YooYo.acl
    def post(self):
        ar = model.User()
        form = self.form()
        
        # 删除
        if self.get_argument('id',False) and self.get_argument('isDel',False):
            ar.remove(self.get_argument('id'))
            return self.write({'success' : True})


        # 验证
        if form.validate(self.request.arguments):
            # 验证通过
            post = form.values()

            if post.get('id',False) :
                ret = ar.edit(post['id'],post)

                return self.write(ret)
            else:
                del post['id']
                ret = ar.add(post)
                return self.write(ret)

class category(Action):
    """栏目"""

    def form(self):
        # 模型列表
        models = model.Model().find().order('id ASC').get(100)
        modelList = []
        for v in models:
            modelList.append({
                'label' : v['info'] ,
                'value' : v['id']
            })

        # 栏目列表
        ar = model.Category()
        treeList = ar.treeToSelect()
        treeList.insert(0,{
            'label' : '无' ,
            'value' : '0'
        })

        form = YooYo.form.Form()
        form.add(YooYo.form.Hidden(
            name = 'id' 
        )).add(YooYo.form.Select(
            name = 'model_id',
            label = '所属模型',
            data = modelList
        )).add(YooYo.form.Select(
            name = 'parent',
            label = '上级',
            data = treeList
        ))
        # 多语言名称
        locales = model.Locale().find().get(100)
        for locale in locales:
            form.add(YooYo.form.Text(
                name = 'locale_' + str(locale['id']) ,
                label = locale['name'] + '名称' ,
                validators = ['notEmpty'] ,
                filter = ['trim']
            ))

        return form.add(YooYo.form.Submit(
            name = 'send' ,
            label = '保存' 
        ))

    @app.plugin.controller.beforeExecute
    @YooYo.acl
    def get(self):
        ar = model.Category()
        data = ar.treeToSelect()
       
        self.render('admin/category.html',data=data,form=self.form().getConfig())
       
    @app.plugin.controller.beforeExecute 
    @YooYo.acl
    def post(self):
        ar = model.Category()
        form = self.form()
        
        # 删除
        if self.get_argument('id',False) and self.get_argument('isDel',False):
            ar.remove(self.get_argument('id'))
            return self.write({'success' : True})


        # 验证
        if form.validate(self.request.arguments):
            # 验证通过
            post = form.values()

            if post.get('id',False) :
                ret = ar.edit(post['id'],post)

                return self.write(ret)
            else:
                del post['id']
                ret = ar.add(post)
                return self.redirect(self.request.uri)


class model_field(Action):
    """模型字段管理"""

    def form(self):
        form = YooYo.form.Form()
        form.add(YooYo.form.Hidden(
            name = 'id' 
        )).add(YooYo.form.Hidden(
            name = 'model_id' 
        )).add(YooYo.form.Text(
            name = 'name' ,
            label = '字段' ,
            validators = ['notEmpty'] ,
            filter = ['trim']
        )).add(YooYo.form.Text(
            name = 'label' ,
            label = '标签' ,
            validators = ['notEmpty'] ,
            filter = ['trim']
        )).add(YooYo.form.Select(
            name = 'widget' ,
            label = '组件' ,
            data = [
                { 'label' : '单行文本框' , 'value' : 'Text' } ,
                { 'label' : '多行文本框' , 'value' : 'Textarea' } ,
                { 'label' : '编辑器' , 'value' : 'Editor' } ,
                { 'label' : '图片上传' , 'value' : 'ImageUpload' } ,
                { 'label' : '组图' , 'value' : 'Photos' } ,
                { 'label' : '视频组' , 'value' : 'Videos' } ,
                { 'label' : '下拉框' , 'value' : 'Select' } ,
                { 'label' : '复选框' , 'value' : 'Checkbox' } ,
            ]
        )).add(YooYo.form.Select(
            name = 'type' ,
            label = '类型' ,
            data = [
                { 'label' : '数字' , 'value' : 'INT' } ,
                { 'label' : '字符' , 'value' : 'VARCHAR' } ,
                { 'label' : '文本' , 'value' : 'TEXT' } ,
                { 'label' : '浮点' , 'value' : 'FLOAT' } ,
            ]
        )).add(YooYo.form.Text(
            name = 'info' ,
            label = '描述' ,
            filter = ['trim']
        )).add(YooYo.form.Textarea(
            name = 'data' ,
            label = '可选数据' ,
            filter = ['trim'] ,
            validators = ['isJson'] 
        )).add(YooYo.form.Textarea(
            name = 'validators' ,
            label = '验证规则' ,
            filter = ['trim'] ,
            validators = ['isJson'] 
        )).add(YooYo.form.Textarea(
            name = 'filters' ,
            label = '过滤规则' ,
            filter = ['trim'] ,
            validators = ['isJson'] 
        )).add(YooYo.form.Text(
            name = 'max_len' ,
            label = '最大长度' ,
            validators = ['isNumber'] ,
            value = '0' ,
        )).add(YooYo.form.Text(
            name = 'min_len' ,
            label = '最小长度' ,
            validators = ['isNumber'] ,
            value = '0' ,
        )).add(YooYo.form.Submit(
            name = 'send' ,
            label = '保存' 
        ))
        return form

    @app.plugin.controller.beforeExecute
    @YooYo.acl
    def get(self,id):
        data = model.Model().get(id)
        fields = model.ModelData().find().where('model_id = ?' , id)\
                                         .get(100)

        self.render('admin/model_field.html',data=data,
                    fields=fields,form=self.form().getConfig())   

    def onFormValidateError(self,element,msg):
        return self.write({
            'success' : False ,
            'msg' : element.label() + ':' + msg
        })
   
    @app.plugin.controller.beforeExecute 
    @YooYo.acl
    def post(self,id):
        ar = model.ModelData()
        form = self.form()
        
        # 删除字段
        if self.get_argument('id',False) and self.get_argument('isDel',False):
            ar.remove(self.get_argument('id'))
            return self.write({'success' : True})

        # 绑定错误回调
        form.on('validateError' , self.onFormValidateError)

        # 验证
        if form.validate(self.request.arguments):
            # 验证通过
            post = form.values()

            if post.get('id',False) :
                ret = ar.edit(post['id'],post)
                #print ret
                return self.write(ret);
            else:
                del post['id']
                post['model_id'] = id
                ret = ar.add(post)
                return self.write(ret);



class models(Action):
    """模型管理"""

    def form(self):
        form = YooYo.form.Form()
        form.add(YooYo.form.Hidden(
            name = 'id' 
        )).add(YooYo.form.Text(
            name = 'title' ,
            label = '表名' ,
            validators = ['notEmpty'] ,
            filter = ['trim']
        )).add(YooYo.form.Text(
            name = 'info' ,
            label = '描述' ,
            validators = ['notEmpty'] ,
            filter = ['trim']
        )).add(YooYo.form.Submit(
            name = 'send' ,
            label = '保存' 
        ))
        return form

    @app.plugin.controller.beforeExecute
    @YooYo.acl
    def get(self):       
       
        data = model.Model().find().order('id ASC').get(10)
        self.render('admin/model.html' , data=data , form=self.form().getConfig())

    @app.plugin.controller.beforeExecute
    @YooYo.acl
    def post(self):
        form = self.form()
        ar = model.Model()
     
        if self.get_argument('id',False) and self.get_argument('isDel',False):
            if int(self.get_argument('id')) == 1:
                return self.write({
                    'success' : False ,
                    'msg' : '文章模型属于系统模型,不允许删除!'
                    })

            ar.remove(self.get_argument('id'))
            return self.write({'success' : True})

        # 验证
        if form.validate(self.request.arguments):
            # 验证通过
            post = form.values()
            
            if post.get('id',False) :
                ar.edit(post['id'],post);
                return self.redirect(self.request.uri)
            else:
                del post['id']
                ar.add(post)
                return self.redirect(self.request.uri)

class locale(Action):
    """语言管理"""

    def form(self):
        form = YooYo.form.Form()
        form.add(YooYo.form.Hidden(
            name = 'id' 
        )).add(YooYo.form.Text(
            name = 'code' ,
            label = '代码' ,
            validators = ['notEmpty'] ,
            filter = ['trim']
        )).add(YooYo.form.Text(
            name = 'name' ,
            label = '名称' ,
            validators = ['notEmpty'] ,
            filter = ['trim']
        )).add(YooYo.form.Submit(
            name = 'send' ,
            label = '保存' 
        ))
        return form

    @app.plugin.controller.beforeExecute
    @YooYo.acl
    def get(self):       

        data = model.Locale().find().order('id ASC').get(10)
        self.render('admin/locale.html' , data=data , form=self.form().getConfig())

    @app.plugin.controller.beforeExecute
    @YooYo.acl
    def post(self):
        form = self.form()
        locale = model.Locale()
     
        if self.get_argument('id',False) and self.get_argument('isDel',False):
            locale.remove(self.get_argument('id'))
            return self.write({'success' : True})

        # 验证
        if form.validate(self.request.arguments):
            # 验证通过
            post = form.values()
            
            if post.get('id',False) :
                locale.find().where('id = ?' , post['id']).save(post);
                return self.redirect(self.request.uri)
            else:
                del post['id']
                locale.find().add(post)
                return self.redirect(self.request.uri)
        


class role(Action):
    '''角色管理'''

    def form(self):
        form = YooYo.form.Form()
        form.add(YooYo.form.Hidden(
            name = 'id' 
        )).add(YooYo.form.Text(
            name = 'code' ,
            label = '名称' ,
            validators = ['notEmpty'] ,
            filter = ['trim']
        )).add(YooYo.form.Text(
            name = 'info' ,
            label = '描述' ,
            filter = ['trim']
        )).add(YooYo.form.Submit(
            name = 'send' ,
            label = '保存' 
        ))
        return form

    @app.plugin.controller.beforeExecute
    @YooYo.acl
    def get(self):       

        role = model.Role().find().order('id ASC').get(10)
        self.render('admin/role.html' , role=role , form=self.form().getConfig())

    @app.plugin.controller.beforeExecute
    @YooYo.acl
    def post(self):
        form = self.form()
        role = model.Role()
     
        if self.get_argument('id',False) and self.get_argument('isDel',False):
            role.remove(self.get_argument('id'))
            return self.write({'success' : True})

        # 验证
        if form.validate(self.request.arguments):
            # 验证通过
            post = form.values()
            
            if post.get('id',False) :
                role.find().where('id = ?' , post['id']).save(post);
                return self.redirect(self.request.uri)
            else:
                del post['id']
                role.find().add(post)
                return self.redirect(self.request.uri)


                

