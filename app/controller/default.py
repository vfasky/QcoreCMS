#coding=utf-8
from app.controller import BaseAction
import os
import datetime
import stat
import mimetypes
import tornado.web
import app.plugin

class index(BaseAction):
    @app.plugin.controller.beforeExecute
    def get(self):
        if self.session.get('test'):
        	self.write(self.session['test'])
        else:
        	self.session['test'] = 'ok'
        	self.write('write')

class pluginStatic(BaseAction):
    """插件的静态目录映射"""
    @tornado.web.asynchronous
    @app.plugin.controller.beforeExecute
    def get(self,plugin,url):
        url = str(url)
        path = os.path.join(self.settings['app_path'] , 'app/plugin/%s/static/' % plugin )
        if os.path.isdir(path) and -1 == url.find('../'):
            self.readFile(os.path.join(path,url))
        else:
            self.write('')
            return self.finish()

    def readFile(self,url):
        if os.path.isfile(url):
            cache_time = 3600 * 24
            stat_result = os.stat(url)
            modified = datetime.datetime.fromtimestamp(stat_result[stat.ST_MTIME])
            self.set_header("Last-Modified", modified)
            mime_type, encoding = mimetypes.guess_type(url)
            if mime_type:
                self.set_header("Content-Type", mime_type)

            self.set_header("Expires", datetime.datetime.utcnow() + \
                                       datetime.timedelta(seconds=cache_time))
            self.set_header("Cache-Control", "max-age=" + str(cache_time))

            fileObj = open(url,'r')
            self.write(fileObj.read())
            fileObj.close()
        else:
            self.write('')
        return self.finish()
        

class PIE(BaseAction):
    '''
    PIE makes Internet Explorer 6-9 capable 
    of rendering several of the most useful 
    CSS3 decoration features.
    @link http://css3pie.com/
    '''

    txt = False
    
    def get(self):
        self.set_header("Content-Type","text/x-component")
        if PIE.txt == False:
            path = os.path.join( self.settings['static_path'] , 'style/PIE.htc')
            fileObj = open(path,'r')
            PIE.txt = fileObj.read()
            fileObj.close()
        self.write(PIE.txt)



class _404(BaseAction):
    @app.plugin.controller.beforeExecute
    def get(self , url):
        self.render('404.html')

    @app.plugin.controller.beforeExecute
    def post(self , url):
        return self.get(url)
