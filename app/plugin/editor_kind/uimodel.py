#coding=utf-8
import app.plugin

class editor_kind(app.plugin.UIModule):

	def css_files(self):
		return [
			self.static_url('js/themes/default/default.css') ,
		]

	def javascript_files(self):
		return [
			self.static_url('js/kindeditor-min.js') ,
			self.static_url('js/lang/zh_CN.js') ,
		]
		
	def render(self):
		return '''
		seajs.use('%s',function(formPlugin){
			formPlugin.init(form);
		});
		''' % self.static_url('js/formPlugin')
	