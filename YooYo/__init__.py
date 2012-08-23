#coding=utf-8
import functools
import YooYo.util as util

def acl(method):

    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        URI  = self.__class__.__module__ + '.' + self.__class__.__name__
        rule = self.settings['acl']
        currentUser = self.get_current_user()
        role = []

        if None == currentUser:
            role.append('ACL_NO_ROLE')
        elif util.validators.isDict(currentUser):
            self._user = currentUser
            if False == currentUser.has_key('roles') or \
               0 == len(currentUser['roles']):
                role.append('ACL_NO_ROLE')
            else:
                role.append('ACL_HAS_ROLE')
                for r in currentUser['roles']:
                    role.append(r)
        #print URI
        #print rule.has_key(URI)

        if rule.has_key(URI):
            if rule[URI].has_key('allow') :
                isPass = False
                for r in rule[URI]['allow'] :
                    if r in role:
                        isPass = True
                        break
                if False == isPass:
                    return self._on_access_denied()
                    #return self.redirect(self.settings['login_url'])
        
        return method(self, *args, **kwargs)
        
    return wrapper