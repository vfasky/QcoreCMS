#coding=utf-8
from app.controller import BaseAction
import os
class index(BaseAction):
    
    def get(self):
        if(self.session.get('test')):
        	self.write(self.session['test'])
        else:
        	self.session['test'] = 'ok'
        	self.write('write')

class PIE(BaseAction):

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

    def get(self , url):
        self.render('404.html')

    def post(self , url):
        return self.get(url)
