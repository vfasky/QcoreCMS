#coding=utf-8

from app.plugin import base
  
class editor_kind(base):
    """
    kind 编辑器
    """   

    def onInstall(self):
        self.bind('app.controller.admin.contentAdd',
                  base.event['beforeRender'],
                  'bindUIModel')

        self.bind('app.controller.admin.contentSave',
                  base.event['beforeRender'],
                  'bindEditor')


    def bindEditor(self):
        self.__kwargs['editor'] = 'editor_kind'