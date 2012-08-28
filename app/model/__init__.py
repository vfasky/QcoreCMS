#coding=utf-8
import YooYo.mvc.Model
import YooYo.util as util
import app.model.meta
import YooYo.form
from YooYo.db.mySql import Database as mysql
from tornado import escape


class Plugin(YooYo.mvc.Model.Base):
    """插件表"""
    # 表名
    table = 'qc_plugin'
    # 主键
    primaryKey = 'id'

    def __init__(self):
        YooYo.mvc.Model.Base.__init__(self)

class CategoryHasArticle(YooYo.mvc.Model.Base):
    """栏目关联文章表"""
    # 表名
    table = 'qc_category_has_article'
    # 主键
    primaryKey = 'id'

    def __init__(self):
        YooYo.mvc.Model.Base.__init__(self)


class Attachment(YooYo.mvc.Model.Base):
    """附件表"""
    # 表名
    table = 'qc_attachment'
    # 主键
    primaryKey = 'id'

    def __init__(self):
        YooYo.mvc.Model.Base.__init__(self)

    def add(self,data):
        data['time'] = util.time.time()
        self.find().add(data)  


class User(YooYo.mvc.Model.Base):
    """会员表"""
    # 表名
    table = 'qc_user'
    # 主键
    primaryKey = 'id'

    def __init__(self):
        YooYo.mvc.Model.Base.__init__(self)

    # 扩展元数据
    def meta(self,attr):
        return app.model.meta.User(self,attr)

    # 只删除权限角色,不删除对应的文章
    def remove(self,id):
        RoleHasUser().find('user_id = ?',id).delete()
        self.find('id = ?' , id).delete()

    def edit(self,id,data):
        #检查账号,邮箱是否唯一
        count = self.find('name = ?' , data['name'])\
                    .where('id != ?' , id)\
                    .count()

        if 0 != count :
            return {
                'success' : False ,
                'msg' : '账号已经存在'
            }

        count = self.find('email = ?' , data['email'])\
                    .where('id != ?' , id)\
                    .count()

        if 0 != count :
            return {
                'success' : False ,
                'msg' : '邮箱已经存在'
            }

        vals = {
            'name' : data['name'] ,
            'email' : data['email'] ,
        }

        if util.validators.isEmpty(data['password']) == False:
            vals['password'] = util.md5(data['password'])

        self.find('id = ?',id).save(vals)

        RoleHasUser().find('user_id = ?',id).delete()

        # 关联角色
        for r in data['roles'] : 
            RoleHasUser().find().add({
                'user_id' : id ,
                'role_id' : r
            })

        return {
            'success' : True
        }

    def add(self,data):
        #检查账号,邮箱是否唯一
        count = self.find('name = ?' , data['name'])\
                    .count()

        if 0 != count :
            return {
                'success' : False ,
                'msg' : '账号已经存在'
            }

        count = self.find('email = ?' , data['email'])\
                    .count()

        if 0 != count :
            return {
                'success' : False ,
                'msg' : '邮箱已经存在'
            }
        
        id = self.find().add({
            'password' : util.md5(data['password']) ,
            'name' : data['name'] ,
            'email' : data['email'] ,
            'time' : util.date.time()
        })

        # 关联角色
        for r in data['roles'] : 
            RoleHasUser().find().add({
                'user_id' : id ,
                'role_id' : r
            })

        return {
            'success' : True
        }


     

class Category(YooYo.mvc.Model.Base):
    """栏目"""
    # 表名
    table = 'qc_category'
    # 主键
    primaryKey = 'id'

    def __init__(self):
        YooYo.mvc.Model.Base.__init__(self)

    # 扩展元数据
    def meta(self,attr):
        return app.model.meta.Category(self,attr)

    # 取栏目对应的类型
    def getModel(self,id):
        table = self.find().join('qc_model AS M ON M.id = qc_category.model_id')\
                           .where('qc_category.id = ?' , id)\
                           .select('M.title')\
                           .get()

        if table:
            return self.use('qc_' + table['title'])
        return False

    # 取所有下级
    @staticmethod
    def getChilds(id):
        childs = Category().find().where('parent = ?' , id)\
                                  .get(100)

        _chiles = []
        for child in childs:
            _chile = child.attr
            _chile['locales'] = child.getLocales()
            _chile['model'] = child.getModel()
            if _chile['childs'] != None:
                _chile['child'] = Category.getChilds(child['id'])
            _chiles.append(_chile)

        return _chiles

    # 取所有分类树
    def getTree(self):
        return Category.getChilds(0)

    # 将树一维化
    def treeToList(self,tree,level=0,temp=[]):
        for child in tree:
            child['level'] = level
            if child['child'] != ',' :
                _tree = child['child']
                del child['child']

                temp.append(child)
                temp = self.treeToList(_tree,level+1,temp)
            else:
                temp.append(child)

        return temp

    def treeToSelect(self,_icon='|-- '):
        _list = self.treeToList(self.getTree(),0,[])
        #print _list
        data = []
        for v in _list:
            icon = _icon
            if v['level'] > 0 :
                for i in range(0,int(v['level'])):
                    icon = '　' + icon
            locale = []
            for i in v['locales']:
                locale.append(i['title'])

            title = icon + '/'.join(locale)

            data.append({
                'label' : title ,
                'value' : v['id'] ,
                'data'  : v
            })
        return data

    def edit(self,id,data):
        # 上级不能是自身
        if str(data['parent']) == str(id):
            return {
                'success' : False ,
                'msg' : '上级不能是自身'
            }

        # 不能移到下级
        count = self.find('id = ?' , data['parent'])\
                    .where('parents LIKE ?' , '%,' + str(id)+',%')\
                    .count()

        if 0 != count :
            return {
                'success' : False ,
                'msg' : '不能移到下级'
            }

        that = self.get(id)

        if that['parent'] != data['parent']:
            #print data['parent']
            if '0' == str(data['parent']):
                thatParent = {
                    'parents' : ',',
                    'childs' : ','
                }
            else:
                thatParent = self.get(data['parent'])


            if that :
               
                #self.find('id = ?' , id).save(data)
                parents = thatParent['parents'] + str(data['parent']) + ','
                childs = that['childs'].strip(',').split(',')
                
                if len(childs) > 0 and childs[0] != '':

                    # 处理下级
                    for c in self.find('id IN ?' , childs).get(500):
                        self.find('id = ?' , c['id']).save({
                            'parents' : c['parents'].replace(that['parents']+str(id) + ',' ,
                                parents + str(id) + ','
                            )
                        })

                # 处理旧上级
                oldParents = that['parents'].strip(',').split(',')
                
                #print oldParents

                if len(oldParents) > 0 and oldParents[0] != '':
                    for p in self.find('id IN ?' , oldParents).get(100):
                        _childs = p['childs']

                        for v in childs:
                            _childs = _childs.replace(',' + str(v) + ',' , ',')

                        self.find('id = ?' , p['id']).save({
                            'childs' : _childs.replace(','+str(id) + ',' ,','
                            )
                        })

                # 处理上级
                newsParents = thatParent['parents'].strip(',').split(',')
                if len(newsParents) > 0 and newsParents[0] != '':
                    for p in self.find('id IN ?' , newsParents).get(100):
                        self.find('id = ?' , p['id']).save({
                            'childs' : p['childs'].replace(','+str(data['parent']) + ',' ,
                                ','+str(data['parent']) + ',' + str(id) + that['childs']
                            )
                        })
                self.find('id = ?' , data['parent']).save({
                        'childs' : that['childs'] + str(id) + ','
                    })

                # 保存自身
                self.find('id = ?' ,id).save({
                    'parent' : data['parent'] ,
                    'parents' : parents ,
                    'model_id' : data['model_id'] ,
                })
        else:
            self.find('id = ?' ,id).save({
                'model_id' : data['model_id'] ,
            })

        # 抽取多语言
        locales = Locale().find().get(100)
        for locale in locales:
            key = 'locale_' + str(locale['id'])
            if data.has_key(key):
                _data = {
                    'title' : data[key]
                }
                CategoryLocale().find('category_id = ?' , id)\
                                .where('locale_id = ?' , locale['id'])\
                                .save(_data)

        return {
            'success' : True
        }





    def add(self,data):
        # 一级目录
        if str(data['parent']) == '0':
            id = self.find().add({
                'childs' : ',' ,
                'parents' : ',0,' ,
                'parent' : 0 ,
                'model_id' : data['model_id']
            })
        # N级目录
        else:
            parent = self.find().where('id = ?' , data['parent']).get()
            if None == parent:
                raise NameError, '上级不存在'

            id = self.find().add({
                'childs' : ',' ,
                'parents' : parent['parents'] + str(parent['id']) + ',',
                'parent' : parent['id'] ,
                'model_id' : data['model_id']
            })
            # 更新直接上级
            self.find().where('id = ?' , parent['id'])\
                       .save({
                            'childs' : parent['childs'] + str(id) + ',',
                        })

            # 更改所有上级的 childs
            index = ',' + str(parent['id']) + ','
            parents = self.find().where('childs LIKE ?' , '%' + index + '%')\
                                 .where('id != ?' , parent['id'])\
                                 .select('id,childs')\
                                 .get(500)

            for p in parents:
                self.find().where('id = ?',p['id'])\
                           .save({
                                'childs' : p['childs'].replace(index, index + str(id) + ',')
                            })


        # 抽取多语言
        locales = Locale().find().get(100)
        for locale in locales:
            key = 'locale_' + str(locale['id'])
            if data.has_key(key):
                _data = {
                    'category_id' : id ,
                    'locale_id' : locale['id'] ,
                    'title' : data[key]
                }
                CategoryLocale().find().add(_data)


    def remove(self,id):
        category = self.get(id)
        if category:
            # 删除下级
            if category['childs'] != ',' :
                childs = self.find('parent = ?' ,id).select('id').get(100);
                for v in childs:
                    self.remove(v['id'])

            # 删除对应的文章
            model = Model().get(category['model_id'])

            if model:
                data = CategoryHasArticle().find('category_id = ?',category['id']).get(100)
                for v in data:
                    self.use('qc_' + model['title']).where('category_has_article_id = ?' , v['id'])\
                                                    .delete()

                for v in data:
                    CategoryHasArticle().find('id = ?',v['id']).delete()

            CategoryLocale().find('category_id = ?' , category['id']).delete()
            self.find('id = ?' , category['id']).delete()

            # 清除上级的 childs
            parents = self.find('childs LIKE ?' , '%,' + str(id) + ',%').get(100)
            for p in parents:
                self.find('id = ?' , p['id']).save({
                        'childs' : p['childs'].replace(',' + str(id) + ',', ',')
                    })

class CategoryLocale(YooYo.mvc.Model.Base):
    """栏目多语言结构"""
    # 表名
    table = 'qc_category_locale'
    # 主键
    primaryKey = 'id'

    def __init__(self):
        YooYo.mvc.Model.Base.__init__(self)



class ModelData(YooYo.mvc.Model.Base):
    """数据模型结构"""
    # 表名
    table = 'qc_model_data'
    # 主键
    primaryKey = 'id'

    # 保留字段
    attr = ['id','model_id','locale_id','ip','category_has_article_id',
            'user_id','time','change_time','listorder']

    def __init__(self):
        YooYo.mvc.Model.Base.__init__(self)



    # 删除字段
    def remove(self,id):
        field = self.get(id)
        model = Model().get(field['model_id'])  

        sql = 'ALTER TABLE `qc_%s` drop %s' 
        sql = sql % (model['title'] , field['name'])
        mysql.execute(sql)

        self.find().where('id = ?',id).delete()

    # 修改字段
    def edit(self, id , data):
        field = self.get(id)

        if data['name'] in ModelData.attr :
            return { 
                'success' : False ,
                'msg' : data['name'] + '是保留字段'
            }

        #检查字段是否存在
        count = self.find().where('name = ?' , data['name'])\
                           .where('id != ?' , id)\
                           .where('model_id = ?',field['model_id'])\
                           .count()

        if count != 0 :
            return { 
                'success' : False ,
                'msg' : '字段已经存在'
            }

        if field['name'] != data['name'] \
           or field['type'] != data['type'] :

            model = Model().get(field['model_id']) 
            sql = 'ALTER TABLE `qc_%s` CHANGE %s %s %s;'

            if int(data['max_len']) != 0 :
                length = '(%s)' % str(data['max_len'])
            else :
                length = ''

            sql = sql % (model['title'] , field['name'] , data['name'] , data['type'] + length)
            mysql.execute(sql)

        self.find().where('id = ?' , id).save(data)

        return { 
            'success' : True
        }

    # 添加字段
    def add(self,data):
        
        model = Model().get(data['model_id']) 

        if data['name'] in ModelData.attr :
            return { 
                'success' : False ,
                'msg' : data['name'] + '是保留字段'
            }

        #检查字段是否存在
        count = self.find().where('name = ?' , data['name'])\
                           .where('model_id = ?',data['model_id'])\
                           .count()

        if count != 0 :
            return { 
                'success' : False ,
                'msg' : '字段已经存在'
            }

        id = self.find().add(data)
        field = self.get(id)
   
        sql = 'ALTER TABLE `qc_%s` Add %s %s%s;'
        if int(field['max_len']) != 0 :
            length = '(%s)' % str(field['max_len'])
        else :
            length = ''

        sql = sql % (model['title'] , field['name'] , field['type'] , length )
        mysql.execute(sql)

        return { 
            'success' : True
        }



class Model(YooYo.mvc.Model.Base):
    """数据模型"""
    # 表名
    table = 'qc_model'
    # 主键
    primaryKey = 'id'

    def __init__(self):
        YooYo.mvc.Model.Base.__init__(self)

    def getForm(self,id):
        def jsonDecode(json,defalut=[]):
            if json == None or '' == json:
                return defalut
            return escape.json_decode(json)

        # ['id','model_id','locale_id','ip','category_id',
        #    'user_id','time','change_time','listorder']

        fields = self.getFields(id)
        form = YooYo.form.Form()

        form.add(YooYo.form.Hidden(
            name = 'id'
        )).add(YooYo.form.Hidden(
            name = 'locale_id' ,
            validators = 'notEmpty'
        )).add(YooYo.form.Hidden(
            name = 'model_id' ,
            value = id ,
            validators = 'notEmpty'
        ))

        for f in fields:
            if hasattr(YooYo.form,f['widget']) :
                form.add(getattr(YooYo.form,f['widget'])(
                    name = f['name'] ,
                    label = f['label'] ,
                    validators = jsonDecode(f['validators']),
                    filter = jsonDecode(f['filters']),
                    data = jsonDecode(f['data'])
                ))
        
        return form

    def getFields(self,id):
        fields = ModelData().find('model_id = ?' , id)\
                            .order('listorder DESC , id ASC')\
                            .get(100)

        return fields


    # 删除模型,并删除对应的表,这操作极有破坏性!
    def remove(self,id):
        model = self.get(id)

        if model :
            # 删除对应的栏目
            categoryModel = Category()
            categorys = categoryModel.find().where('model_id = ?' , id).get(100)
            for v in categorys:
                categoryModel.remove(v['id'])

            # 删除对应的表
            sql = 'DROP TABLE IF EXISTS qc_%s ;' % model['title']
            mysql.execute(sql)

            # 删除模型
            ModelData().find('model_id = ?' ,id).delete()
            self.find().where('id = ?' , id).delete()


    # 添加模型,生成对应的表
    def add(self,data):
        id = self.find().add(data)
        model = self.get(id)

        if model : 
            # 复制文章表结构
            modelData = ModelData()
            fields = modelData.find().where('model_id = ?' , 1).get(100)
            for v in fields:
                v['model_id'] = id
                del v['id']
                modelData.find().add(v)

            self.createTable(id)

    # 更改模型
    def edit(self,id,data):
        model = self.get(id)

        if model : 
            self.find().where('id = ?' , id).save(data)

            if model['title'] != data['title'] :
                sql = 'alter table qc_%s rename qc_%s;'
                sql = sql % (model['title'] , data['title'])
                mysql.execute(sql)



    # 根据字段结构,生成sql
    def buildFieldSql(self,id):
        fields = ModelData().find().where('model_id = ?' , id)\
                                   .get(100)   

        def _buildSql(field):
            
            if int(field['max_len']) != 0 :
                length = '(%s)' % str(field['max_len'])
            else :
                length = ''

            return "`%s` %s%s NULL ,\r\n" % (field['name'] , field['type'] , length)

        data = []

        for field in fields:
            data.append( _buildSql(field) )

        return ''.join(data)


    '''
    根据字段结构,生成表
    '''
    def createTable(self,id):
        
        data = self.get(id)
        if data :
            sql = '''CREATE TABLE IF NOT EXISTS `qc_%s` (
                      `id` INT NOT NULL AUTO_INCREMENT ,
                      `model_id` INT NULL ,
                      `locale_id` INT NULL ,
                      `category_has_article_id` INT NULL ,
                      `ip` VARCHAR(15) NULL ,
                      `user_id` INT NOT NULL ,
                      `time` INT NOT NULL ,
                      `change_time` INT NOT NULL ,
                      `listorder` INT NOT NULL DEFAULT 0 ,
                      %s
                      PRIMARY KEY (`id`) ,
                      INDEX `IX_model_locale` (`model_id` DESC , `locale_id` DESC , `category_has_article_id` DESC) )
                    ENGINE = InnoDB;'''

            table = data['title']
            sql = sql % ( table , self.buildFieldSql(id) )

            return mysql.execute(sql)


class RoleHasUser(YooYo.mvc.Model.Base):
    """用户角色关联"""
    # 表名
    table = 'qc_role_has_user'
    # 主键
    primaryKey = 'id'

    def __init__(self):
        YooYo.mvc.Model.Base.__init__(self)

class Locale(YooYo.mvc.Model.Base):
    """语言种类"""
    # 表名
    table = 'qc_locale'
    # 主键
    primaryKey = 'id'

    def __init__(self):
        YooYo.mvc.Model.Base.__init__(self)


class Role(YooYo.mvc.Model.Base):
    '''
    角色表
    '''
    # 表名
    table = 'qc_role'
    # 主键
    primaryKey = 'id'

    def __init__(self):
        YooYo.mvc.Model.Base.__init__(self)

    # 移除角色
    def remove(self,id):
        RoleHasUser().find().where('role_id = ?' , id).delete()
        self.find().where('id = ?', id).delete()
        return True

