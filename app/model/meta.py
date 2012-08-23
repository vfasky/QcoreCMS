#coding=utf-8
import YooYo.mvc.Model
import YooYo.util as util
import app.model

class User(YooYo.mvc.Model.Meta):
	"""会员表"""
	
	def getRoles(self):
		ar = app.model.RoleHasUser().find()\
		              .join('qc_role AS R ON R.id = qc_role_has_user.role_id')\
		              .select('R.code,R.info,R.id')\
		              .where('qc_role_has_user.user_id = ?' , self['id'])

		return ar.get(20)

	def getRoleCodes(self):
		roles = self.getRoles()
		codes = []
		for role in roles:
			codes.append(role['code'])
		return codes
		

class Category(YooYo.mvc.Model.Meta):
	'''栏目表'''

	def getLocale(self,id):
		ar = app.model.CategoryLocale().find()\
		              .where('category_id = ?' , self['id'])\
		              .where('locale_id = ?',id)\
		              .select('title')\
		              .get()

		if ar:
			return ar['title']
		return ar

	def getModel(self):
		ar = app.model.Model().find().where('id = ?', self['model_id'])
		return ar.get()

	def getLocales(self):
		locales = app.model.Locale().find().select('id').order('id ASC').get(100)
		ar = app.model.CategoryLocale().find()\
		              .where('category_id = ?' , self['id'])

		ids = []
		for locale in locales:
			ids.append(str(locale['id']))

		return ar.where('locale_id IN ?', ids ).get(100)



