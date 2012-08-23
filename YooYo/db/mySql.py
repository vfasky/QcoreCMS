#coding=utf-8
__author__ = 'vfasky@gmail.com'

from YooYo.db import Query
import random
import MySQLdb
from YooYo.util import validators

def use(table):
    return Database(table)

'''
  to tornado 的适配
'''
class Database(Query):
    
    # 连接池
    pool = {
        'WRITE' : [] ,
        'READER' : []
    }

    # 将连接加入连接池
    @staticmethod
    def addConnect(connection , action=False):
        if action == False :
            Database.pool['WRITE'].append(connection)
            Database.pool['READER'].append(connection)
        else:
            if Database.pool.has_key(action):
                Database.pool[action].append(connection)

    @staticmethod
    def execute(sql, *param):
        return Database.pool['WRITE'][0].execute(sql,*param)


    def __init__(self, table):
        Query.__init__(self, table)
        # 元数据绑定
        self.Meta = False

    # 从连接池取连接
    def getConnect(self, action=False):
        #print self._action
        if False == action:
            action = self._action

        if action == 'SELECT':
            count = len(Database.pool['READER'])
            if 1 == count :
                return Database.pool['READER'][0]
            elif count > 1 :
                key = random.randint(0 , int(count) - 1)
                return Database.pool['READER'][key]

        else:
            count = len(Database.pool['WRITE'])
            if 1 == count :
                return Database.pool['WRITE'][0]
            elif count > 1 :
                key = random.randint(0 , int(count) - 1)
                return Database.pool['WRITE'][key]

    def count(self):
        ret = Query.count(self)
        self._sql = ret['sql']
        data = self.getConnect().get(ret['sql'] , *ret['param'])
        if data :
            return data.row_count
        return 0

    # 取分页信息
    def getPagination(self):
        if None == self._page :
            return {}

        import math

        #总数量
        count = self.count()
        #总页数
        countPage = math.ceil( float(count) / float(self._pageSize) ) 

        #前一页
        if self._page <= 1 :
            prev = 1
        else:
            prev = self._page -1
        #下一页
        if self._page < countPage:
            next = self._page + 1
        else:
            next = countPage

        return {
            'prev' : int(prev) ,
            'next' : int(next) ,
            'current' : self._page ,
            'countPage' : int(countPage) ,
            'count' : int(count)
        }

    def where(self , condition , *arguments):
        '''与查询条件'''
        condition  = str(condition).strip()
        conditions = condition.split(' ')
        where      = ''
        isIn = False
        for v in conditions:
            _v = self.filterColumn(v)
            if 'IN' == _v : isIn = True
            where += _v + ' '

        if isIn :
            for arg in arguments :
                if validators.isArray(arg):
                    arg = map(MySQLdb.escape_string,arg)
                    arg = '(' + ','.join(arg) + ')'
                else:
                    arg = MySQLdb.escape_string(arg)

            where = where % (arg)   


        else :    
            for v in arguments:
                self._param['where'].append(v)

        where = len(self._where) > 0 and ' AND ( ' + where + ') ' or ' ( ' +where + ') '

        self._where.append( where )
        #print self._where
        
        #print self._param['where'] 
        return self

    def orWhere(self , condition , *arguments):
        '''与查询条件'''
        condition  = str(condition).strip()
        conditions = condition.split(' ')
        where      = ''
        isIn = False

        for v in conditions:
            _v = self.filterColumn(v)
            if 'IN' == _v : isIn = True
            where += _v + ' '

        if isIn :
            for arg in arguments :
                if validators.isArray(arg):
                    arg = map(MySQLdb.escape_string,arg)
                    arg = '(' + ','.join(arg) + ')'
                else:
                    arg = MySQLdb.escape_string(arg)

            where = where % (arg)   


        else :    
            for v in arguments:
                self._param['where'].append(v)

        where = len(self._where) > 0 and ' OR ( ' + where + ') ' or ' ( ' +where + ') '

        self._where.append( where )
     
        return self 

    def delete(self):
        ret = Query.delete(self)
        self._sql = ret['sql']
        return self.getConnect().execute(ret['sql'] , *ret['param'])

    def save(self , attr):
        ret = Query.save(self , attr)
        self._sql = ret['sql']
        #print ret['param']
        return self.getConnect().execute(ret['sql'] , *ret['param'])

    def add(self , attr):
        ret = Query.add(self , attr)
        self._sql = ret['sql']
        #print ret['param']
        return self.getConnect().execute(ret['sql'] , *ret['param'])



    def query(self):
        ret = self.sql()
        #print ret['param']
        self._sql = ret['sql']
        data = self.getConnect().query(ret['sql'] , *ret['param'])
        if False == self.Meta:
            return data

        ret = []
        for v in data:
            ret.append(self.Meta(v))
        return ret

    # 取指定条数的数据
    def get(self , number=1):
        ret = self.limit(number).sql()
        self._sql = ret['sql']
        if 1 == number:
            #print ret['sql']

            data = self.getConnect().get(ret['sql'] , *ret['param'])
            if None != data:
                return False == self.Meta and data or self.Meta(data) 
            return data
        #print ret['sql']
        data = self.getConnect().query(ret['sql'] , *ret['param'])
        if False == self.Meta:
            return data

        ret = []

        for v in data:
            ret.append(self.Meta(v))
        return ret

    
