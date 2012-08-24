#coding=utf-8
import uuid
import time

import YooYo.db.mySql as mySql
import YooYo.util as util


class Memory:
    """基于内存的session"""

    mm = {}

    @staticmethod
    def getData(sessionId):
        try:    
            data = Memory.mm.get('__SESSION__' + sessionId,False)

            
            if data and data.has_key('__time__') :
                thisTime = int(time.time())
                interval = thisTime - data['__time__']

                if data['__leftTime__'] - interval <= 0 :
                    Memory.deleteData(sessionId)
                    return {}

                # 维持生命周期
                if data['__leftTime__'] - interval < data['__leftTime__'] / 2 :
                    #print 'updata'
                    Memory.setData(sessionId, data, data['__leftTime__'])

            return data and data or {}
        except Exception, e:
            return {}

    @staticmethod
    def setData(sessionId , data , leftTime = 1800):
        data['__time__'] = int(time.time())
        data['__leftTime__'] = int(leftTime)
        Memory.mm['__SESSION__' + sessionId ] = data

    @staticmethod
    def deleteData(sessionId):
        if Memory.mm.has_key('__SESSION__' + sessionId):
            del Memory.mm['__SESSION__' + sessionId]

    def __init__(self, sessionId = False, leftTime = 1800):
        if False == sessionId:
            sessionId = str(uuid.uuid4())
        self.sessionId = sessionId
        self.leftTime  = int(leftTime)
        self.data = Memory.getData(self.sessionId)

    # 返回 session id
    def id(self):
        return self.sessionId

    # 设置session
    def set(self , key , value):
        self.data[key] = value
        Memory.setData(self.sessionId, self.data, self.leftTime)

    # 取值
    def get(self , key):
        if self.data.has_key(key):
            return self.data[key]
        return None

    # 删除值
    def delete(self , key):
        if self.data.has_key(key):
            del self.data[key]
            Memory.setData(self.sessionId, self.data, self.leftTime)

    # 清空
    def clear(self):
        self.data = {}
        Memory.deleteData(self.sessionId)

    def __getitem__(self, key):
        return self.get(key)

    def __setitem__(self, key, value):
        return self.set(key , value)

    def __delitem__(self, key):
        return self.delete(key)

    def __len__(self):
        return len(self.data.keys())

    def __str__(self):
        return self.data

    def keys(self):
        return self.data.keys()

class MySql:
    """基于mysql的session"""

    table = 'qc_session'

    @staticmethod
    def getData(sessionId):
        thisTime = int(time.time())
        data = mySql.use(MySql.table).where('id = ?',sessionId).get()

        if data :
            if data['time_out'] < thisTime :
                mySql.use(MySql.table).where('id = ?',sessionId).delete()
                return {}

            # 维持生命周期
            if int(data['time_out']) - thisTime < int(data['left_time']) / 2:
                mySql.use(MySql.table).where('id = ?',sessionId).save({
                    'time_out' : thisTime + int(data['left_time'])
                })

            session = util.json.decode(data['values'], {})

            # 退出其它用户
            if session.get('current_user' , False) :
                if session['current_user'].get('userId' , False) :
                    mySql.use(MySql.table).where('id != ?',sessionId)\
                                          .where('user_id = ?',session['current_user']['userId'])\
                                          .delete()

            return session

        return {}

    @staticmethod
    def setData(sessionId , data , leftTime = 1800):
        thisTime = int(time.time())
        userId = 0
        if data.get('current_user' , False) :
            if data['current_user'].get('userId' , False) :
                userId = data['current_user']['userId']

        
        if 0 == mySql.use(MySql.table).where('id = ?',sessionId).count() :
            mySql.use(MySql.table).add({
                'time_out' : thisTime + int(leftTime) ,
                'left_time' : leftTime ,
                'user_id' : userId ,
                'id' : sessionId ,
                'values' : util.json.encode(data)
            })
        else:
            mySql.use(MySql.table).where('id = ?',sessionId).save({
                'time_out' : thisTime + int(leftTime) ,
                'left_time' : leftTime ,
                'user_id' : userId ,
                'values' : util.json.encode(data)
            })
        
    @staticmethod
    def deleteData(sessionId):
        mySql.use(MySql.table).where('id = ?',sessionId).delete()

    def __init__(self, sessionId = False, leftTime = 1800):
        if False == sessionId:
            sessionId = str(uuid.uuid4())
        self.sessionId = sessionId
        self.leftTime  = int(leftTime)
        self.data = MySql.getData(self.sessionId)

    # 返回 session id
    def id(self):
        return self.sessionId

    # 设置session
    def set(self , key , value):
        self.data[key] = value
        MySql.setData(self.sessionId, self.data, self.leftTime)

    # 取值
    def get(self , key):
        return self.data.get(key,None)
   

    # 删除值
    def delete(self , key):
        if self.data.has_key(key):
            del self.data[key]
            MySql.setData(self.sessionId, self.data, self.leftTime)

    # 清空
    def clear(self):
        self.data = {}
        MySql.deleteData(self.sessionId)

    def __getitem__(self, key):
        return self.get(key)

    def __setitem__(self, key, value):
        return self.set(key , value)

    def __delitem__(self, key):
        return self.delete(key)

    def __len__(self):
        return len(self.data.keys())

    def __str__(self):
        return self.data

    def keys(self):
        return self.data.keys()
        


class Memcache:
    '''基于memcache的session'''

    mc = False

    @staticmethod
    def setStorage(mc):
        Memcache.mc = mc

    @staticmethod
    def getData(sessionId):
        try:    
            data = Memcache.mc.get('__SESSION__' + sessionId )
            # 维持生命周期
            if data and data.has_key('__time__') :
                thisTime = int(time.time())
                interval = thisTime - data['__time__']

                if data['__leftTime__'] - interval < data['__leftTime__'] / 2 :
                    #print 'updata'
                    Memcache.setData(sessionId, data, data['__leftTime__'])

            return data and data or {}
        except Exception, e:
            return {}

    @staticmethod
    def setData(sessionId , data , leftTime = 1800):
        data['__time__'] = int(time.time())
        data['__leftTime__'] = int(leftTime)
        Memcache.mc.set('__SESSION__' + sessionId , data , leftTime)
        
    @staticmethod
    def deleteData(sessionId):
        Memcache.mc.delete('__SESSION__' + sessionId)

    def __init__(self, sessionId = False, leftTime = 1800):
        if False == sessionId:
            sessionId = str(uuid.uuid4())
        self.sessionId = sessionId
        self.leftTime  = int(leftTime)
        self.data = Memcache.getData(self.sessionId)

    # 返回 session id
    def id(self):
        return self.sessionId

    # 设置session
    def set(self , key , value):
        self.data[key] = value
        Memcache.setData(self.sessionId, self.data, self.leftTime)

    # 取值
    def get(self , key):
        if self.data.has_key(key):
            return self.data[key]
        return None

    # 删除值
    def delete(self , key):
        if self.data.has_key(key):
            del self.data[key]
            Memcache.setData(self.sessionId, self.data, self.leftTime)

    # 清空
    def clear(self):
        self.data = {}
        Memcache.deleteData(self.sessionId)

    def __getitem__(self, key):
        return self.get(key)

    def __setitem__(self, key, value):
        return self.set(key , value)

    def __delitem__(self, key):
        return self.delete(key)

    def __len__(self):
        return len(self.data.keys())

    def __str__(self):
        return self.data

    def keys(self):
        return self.data.keys()


        