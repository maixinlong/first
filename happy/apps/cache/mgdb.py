#-*- coding:utf-8 -*-
"""
线上存储格式
按微博类型存在不同表中，根据表的skip属性查找上下文数据
author:xiaomai
"""


import pymongo
import bson
##bson.objectid.ObjectId(unicode(value))
con = pymongo.Connection()
db = con.datas
db2 = con.datas_key


def save(types,datas):
    """
    @params types:微博类型
    @params datas:{'aa':[]}
    """
    obj = ''
    num = 0 
    if types in ['fine','video','amuse','dynamic']:
        obj = db[types].insert(datas)
    print 'save success...'


def get(num=-1,types=None,new=False):
    """
    @params num:num 越大表示数据越新
    ＠params types:微博类型
    @return :datas,next_num
    """
    datas = {}
    if types not in ['fine','video','amuse','dynamic']:
        return datas,-2
    count = db[types].find().count()
    num = int(num)
    if num >= count or count <= 0:
        return {},-1

    if new:
        datas = db[types].find().skip(count-1)[0]
	return datas,count-1

    if num < 0:
        return datas,num
    else:
        datas = db[types].find().skip(num)[0]
    return datas,num-1


if __name__ == "__main__":
    for i in range(1,1000000):
        save('fine',{'data1':[{'aa':'a1'},{'bb':'b1'},{'cc':'c1'}],'count':i})


    for j in range(5555,5556):
        datas,next_num = get(num=j,types='fine')
        print next_num
        print datas
