#coding=utf-8
__author__ = 'vfasky@gmail.com'

from YooYo.util import validators

class Query:
    '''
    构造 mysql 查询语句
    ============================

    Python :
    -------------------

        from YooYo.db import Query

        query = Query('test')
        query.where('id = ?' , 1).select('user , sex').sql()

    方法 :
    -------------------

     - join \ leftJoin \ rightJoin `关联查询`
     - select `选择字段`
     - where \ orWhere `查询条件`     
     - group `分组查询`
     - page `分页查询`
     - order `排序`
     - sql `返回查询语句`
     - count `返回统计语句`
     - add `返回添加语句`
     - save `返回更新语句`
     - delete `返回删除语句`

    '''
    def __init__(self, table):
        self._select   = '*'
        self._from     = table
        self._where    = []
        self._join     = []
        self._group    = False
        self._limit    = 0
        self._offset   = 1
        self._order    = False
        self._sql      = ''
        self._attr     = []
        self._action   = 'SELECT'
        self._page     = None
        self._pageSize = None

        self._param  = {
            'where' : [] ,
            'attr' : [] ,
        }

        # 不做处理的字符
        self._condition = ['AND' , '=' , '!=' , '<>' , 
                          '>=' , '>' , '<=' , '<' , 'DESC' ,
                          'IN' , 'OR' , '(' , ')' , 'ASC' ,
                          'ON' , 'AS' , '+' , '-' , 'LIKE' ,
                          'GROUP' , 'ORDER' , 'BY' , ',' ,
                          'COUNT' , '*' , 'MD5' , 'SUM'  ]

    def filterColumn(self, field):
        '''字段加 `` '''

        field = str(field).strip()

        if validators.isNumber(field):
            return field
    
        if '?' == field :
            return '%s'

        if field.upper() not in self._condition:
            temp  = field.split(' ')
            count = len(temp)
            if count == 1 :
                temp2 = field.split('.')
                if len(temp2) == 1 :
                    return '`' + field + '`'

                return '`' + temp2[0] + '`.`' + temp2[1] + '`'

            # 处理 AS 
            elif count == 3:    
                temp2 = temp[0].split('.')
                if len(temp2) == 1 :
                    return '`' + temp[0] + '` ' +  temp[1] + ' `' + temp[2] + '`'
                # 处理 t.id AS ID
                else:
                    return '`' + temp2[0] + '`.`' + temp2[1] + '` ' +  temp[1] + ' `' + temp[2] + '`'

        return field.upper()

    def join(self , join):
        '''内连'''
        join = str(join).strip().split(' ')
        temp = []
        for v in join:
            temp.append( self.filterColumn(v) )
        self._join.append('INNER JOIN ' + ' '.join(temp) + ' ')
        #print self._join
        return self

    def leftJoin(self , join):
        '''左连'''
        join = str(join).strip().split(' ')
        temp = []
        for v in join:
            temp.append( self.filterColumn(v) )
        self._join.append('LEFT JOIN ' + ' '.join(temp) + ' ')
        #print self._join
        return self

    def rightJoin(self , join):
        '''右连'''
        join = str(join).strip().split(' ')
        temp = []
        for v in join:
            temp.append( self.filterColumn(v) )
        self._join.append('RIGHT JOIN ' + ' '.join(temp) + ' ')
        #print self._join
        return self

    def select(self , fields):
        '''选择字段'''
        self._action = 'SELECT'

        fields  = str(fields).split(',')
        select = []
        for v in fields:
            select.append( self.filterColumn(v) )
        self._select = ','.join(select)
        #print self._select
        return self

    def where(self , condition , *arguments):
        '''与查询条件'''
        condition  = str(condition).strip()
        conditions = condition.split(' ')
        where      = ''

        for v in conditions:
            where += self.filterColumn(v) + ' '

        where = len(self._where) > 0 and ' AND ( ' + where + ') ' or ' ( ' +where + ') '

        self._where.append( where )
        #print self._where
        for v in arguments:
            self._param['where'].append(v)
        #print self._param['where'] 
        return self

    def orWhere(self , condition , *arguments):
        '''与查询条件'''
        condition  = str(condition).strip()
        conditions = condition.split(' ')
        where      = ''

        for v in conditions:
            where += self.filterColumn(v) + ' '

        where = len(self._where) > 0 and ' OR ( ' + where + ') ' or ' ( ' +where + ') '

        self._where.append( where )
        #print self._where
        for v in arguments:
            self._param['where'].append(v)
        #print self._param['where'] 
        return self 

    def limit(self , offset = 1, limit = 0):
        self._offset = int(offset)
        self._limit  = int(limit)

        #print self._offset
        #print self._limit

        return self

    def page(self , page = 1 , pageSize = 10):
        '''分页查询'''
        self._page = int(page)
        self._page = self._page < 0 and 1 or self._page
        self._pageSize = int(pageSize)
        #print  self._page 
        return self.limit( self._pageSize , ( self._page - 1 ) *  self._pageSize )


    def group(self , group):
        '''分组查询'''
        groups = str(group).strip().split(',')
        temp = []
        for v in groups:
            temp.append( self.filterColumn(v) )
        self._group = ','.join(temp)
        #print self._group

        return self

    def order(self , order):
        '''排序'''
        orders = str(order).strip().split(',')
        temp = []
        for v in orders:
            temp2 = v.strip().split(' ')

            if len(temp2) > 2:
                order = []
                for v1 in temp2:
                    order.append( self.filterColumn(v1) )
                temp.append( ' '.join(order) )
            else:
                temp2[0] = self.filterColumn(temp2[0])
                if 1 == len(temp2) :
                    temp2.append('ASC')
                temp.append(temp2[0] + ' ' + temp2[1])
        self._order = ','.join(temp)

        #print self._order

        return self

    def add(self , attr):
        # 添加
        self._action = 'INSERT'

        for k in attr :
            self._param['attr'].append(attr[k])
            self._attr.append(self.filterColumn(k))
    
        return self.sql()

    def save(self , attr):
        # 编辑
        self._action = 'UPDATE'

        for k in attr :
            self._param['attr'].append(attr[k])
            self._attr.append(self.filterColumn(k))

        return self.sql()

    def delete(self):
        # 删除
        self._action = 'DELETE'
        return self.sql()
    

    def count(self):
        # 统计查询
        sql = ['SELECT COUNT(*) as `row_count` FROM ' + self.filterColumn( self._from )]
        for v in self._join:
            sql.append(v)

        if len(self._where) > 0 :
            sql.append('WHERE (' + ' '.join(self._where) + ')')

        if False != self._group :
            sql.append('GROUP BY ' + self._group)


        return {
            'sql' : ' '.join(sql) ,
            'param' : self._param['where']
        }
    
    def sql(self):
        # 查询
        sql = []    
        if self._action == 'SELECT' :
            sql.append('SELECT ' + self._select + ' FROM ' + self.filterColumn( self._from ) )

            for v in self._join:
                sql.append(v)

            if len(self._where) > 0 :
                sql.append('WHERE (' + ' '.join(self._where) + ')')

            if False != self._group :
                sql.append('GROUP BY ' + self._group)

            if False != self._order :
                sql.append('ORDER BY ' + self._order)

            sql.append('LIMIT ' + str(self._limit) + ' , ' + str(self._offset) )
        # 写入
        elif self._action == 'INSERT':
            sql.append('INSERT INTO ' + self.filterColumn( self._from ) + ' (')
            sql.append(','.join(self._attr) + ') VALUES (')
            # 点位符 
            placeholder = []

            for v in self._attr:
                placeholder.append('%s')

            sql.append( ','.join(placeholder) + ')' )

        # 更新
        elif self._action == 'UPDATE':
            sql.append('UPDATE ' + self.filterColumn( self._from ) + ' SET')
            columns = [];
            for v in self._attr:
                columns.append( v + '= %s' )
            sql.append( ','.join(columns) )

            if len(self._where) > 0 :
                sql.append('WHERE (' + ' '.join(self._where) + ')')

        # 删除
        elif self._action == 'DELETE':
            sql.append('DELETE FROM ' + self.filterColumn( self._from ))
            if len(self._where) > 0 :
                sql.append('WHERE (' + ' '.join(self._where) + ')')

        param = []
        for v in self._param['attr']:
            param.append(v)

        for v in self._param['where']:
            param.append(v)

        return {
            'sql' : ' '.join(sql) ,
            'param' : param
        }

