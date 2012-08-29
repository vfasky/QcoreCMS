#coding=utf-8

from app.plugin import base
  
class editor_kind(base):
    """
    kind 可视化编辑器 , 在编辑文章时提供上传,可视化编辑功能
    """   

    def onInstall(self):
        self.bind('app.controller.admin.contentAdd',
                  'beforeRender',
                  'bindEditor')

        self.bind('app.controller.admin.contentEdit',
                  'beforeRender',
                  'bindEditor')


    def bindEditor(self):
        self._context['kwargs']['editor'] = 'editor_kind'
        return False