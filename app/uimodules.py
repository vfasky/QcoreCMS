#coding=utf-8
__author__ = 'vfasky'

import tornado.web
import Image
import os
import app.model as model
import app.plugin

class UIModule(tornado.web.UIModule):
    plugins = False

    def __init__(self, handler):
        tornado.web.UIModule.__init__(self, handler)
        self._head = []
        self._body = []

    def html_head(self):
        return ''.join(self._head)

    def html_body(self):
        return ''.join(self._body)
    
    def render(self, *args, **kwargs):
        if False == UIModule.plugins:
            UIModule.plugins = model.Plugin().find('type = ?' , 'UIModule').get(500)

        name = self.__class__.__name__

        # 渲染之前执行
        for plugin in UIModule.plugins:
            if plugin['name'] == name \
            and plugin['event'] == 'before' \
            and hasattr(app.plugin.UIModule,plugin['plugin']) :

                plug = getattr(app.plugin.UIModule,plugin['plugin'])(self, *args, **kwargs)
                ret = plug.execute(plugin['action'])

                self._head.append(plug.htmlHead())
                self._body.append(plug.htmlBody())

                if False == ret:
                    return False

                self = ret['self']
                args = ret['args']
                kwargs = ret['kwargs']

        ret = self.execute(*args, **kwargs)

        # 渲染之后执行
        for plugin in UIModule.plugins:
            if plugin['name'] == name \
            and plugin['event'] == 'after' \
            and hasattr(app.plugin.UIModule,plugin['plugin']) :

                plug = getattr(app.plugin.UIModule,plugin['plugin'])(self, *args, **kwargs)
                ret = plug.execute(plugin['action'],ret)

                self._head.append(plug.htmlHead())
                self._body.append(plug.htmlBody())

        return ret

        


class thumbnail(UIModule):
    '''
    动态生成缩略图
    =============
    demo :
    
    {% module thumbnail('/static/file/2012-08/f6052cf59f0d82928970d4ed61f09255.jpg',width=120,height=90) %}
    '''

    def getExt(self, url):
        fileInfo = str(url).split('.')
        return fileInfo[ len(fileInfo) - 1 ]


    def execute(self, url, width=100, height=100, default='/static/none.png'):
       
        imgPath = os.path.join(self.handler.settings['app_path'] , '.' + url)
        thumbnailName = '_tb_' + str(width) + '_' + str(height) + '.' + self.getExt(url)
        thumbnailPath = imgPath + thumbnailName
        # 缩略图存在,直接返回
        if os.path.isfile(thumbnailPath):
            return url + thumbnailName

        if os.path.isfile(imgPath):
            img = Image.open(imgPath)
            tbImg = img.resize((width,height))
            tbImg.save(thumbnailPath)
            return url + thumbnailName

        return default
        

class adminPagination(tornado.web.UIModule):
    '''
    后台分页条
    '''
    def render(self, pagination, url=None, key='page', maxItem=10):
        if not url:
            url = self.request.path

        if url.find('?') != -1:
            link = url + '&' + key + '='
        else:
            link = url + '?' + key + '='

        list = []
        if pagination['countPage'] > maxItem:
            import math

            # 左右个数
            itemCount = int(math.floor((maxItem - 3) / 2))

            # 开头
            list.append({'name': '1', 'class': '', 'url': link + '1'})

            pageCount = pagination['countPage'] > itemCount and  itemCount or pagination['countPage']
            # 确定起始号码;
            pageBegin = ( pagination['current'] - itemCount ) < 2 and  2 or ( pagination['current'] - itemCount )
            pageEnd = ( pagination['current'] + itemCount ) > pagination['countPage'] and  pagination['countPage'] or (
                pagination['current'] + itemCount )

            if pageEnd < maxItem:
                pageEnd = maxItem

            if pageBegin != 2:
                list.append({'name': '...', 'class': 'disabled', 'url': '#'})

            for i in range(pageBegin, pageEnd + 1):
                list.append({'name': str(i), 'class': '', 'url': link + str(i)})

            if pageEnd < pagination['countPage']:
                list.append({'name': '...', 'class': 'disabled', 'url': '#'})
                list.append(
                        {'name': str(pagination['countPage']), 'class': '', 'url': link + str(pagination['countPage'])})
        else:
            for i in range(1, int(pagination['countPage']) + 1):
                list.append({'name': str(i), 'class': '', 'url': link + str(i)})
        return self.render_string("admin/pagination.html", pagination=pagination, list=list, link=link)