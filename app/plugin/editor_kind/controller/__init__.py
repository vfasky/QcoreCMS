#coding=utf-8
import app.plugin
import urllib2, urllib
class default(app.plugin.Action):
    '''
    插件的前台控制器(无权限控制)
    '''
    def get(self):
        kw = self.get_argument('kw',False)
        if kw :
            api_url = 'http://tool.phpcms.cn/api/get_keywords.php'
            data = {
                'siteurl' : 'http://127.0.0.1/', 
                'charset' : 'gbk' ,
                'data' : kw.decode('utf8').encode('gbk') ,
                'number' : 3
            }

            try:
                http = urllib2.urlopen(
                    url   = api_url,
                    data  = urllib.urlencode(data)
                    )
                self.write(unicode(http.read(),'gbk').encode("utf8"))
            except Exception, e:
                self.write('')
            


    def post(self):
        pass

class admin(app.plugin.Action):
    '''
    插件的后台控制器
    '''
    def get(self):
        pass

    def post(self):
        pass
    
