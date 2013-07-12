#-*- coding:utf-8 -*-
"""
线上存储格式
按微博类型存在不同表中，根据表的skip属性查找上下文数据
author:xiaomai
"""


import pymongo
import bson
import datetime


print 'mmmmmmmmmmmmmmmmm'
##bson.objectid.ObjectId(unicode(value))
con = pymongo.Connection()
db = con.data    
db2 = con.datas_key
db_ver = con.datas_ver
today = str(datetime.date.today())


def save(types,data):
    """
    @params types:微博类型
    @params data:{评论标记，微博内容，提交日期}
	data = {'comment':'','weibo':{},'date':'07-10'}
    """
    con = pymongo.Connection()
    print 'con',con
    db = con.datas
    db2 = con.datas_key
    db_ver = con.datas_ver
    today = str(datetime.date.today())
    if not types or not data:
        return
    if types not in ['fine','video','amuse','dynamic']:
        return
    #datas = {'07-10':[data1,data2]}
    datas = db[types].find_one({'time':today})[0]
    if datas:
		datas.update({'time':today},{'$push':{'datas':data}})
    else:
        datas = {'time':today,'datas':data}
        obj = db[types].insert(datas)
    #版本号更新
    set_ver(types):
    print 'save success...'


def get(num=-1,types=None):
    """
    @params num:num 越大表示数据越新
    @params types:微博类型
    @return :datas,next_num
    """
    datas = {}
    if types not in ['fine','video','amuse','dynamic']:
        return datas,-2

    count = db[types].find().count()
    num = int(num)
    if num >= count or count <= 0:
        return {},-1

    if num <= 0:
        return datas,num
    else:
        datas = db[types].find().skip(num)[0]
    return datas,num-1

def get_update_first():
    """
	初次加载
	"""
    data = db[types].find_one({'time':today})
    if data:
        datas = datas[0]['datas']
    else:
        d = db[types].find()
        count = d.count()
        datas = d.skip(count-1)[0]['datas']
    return datas,len(datas)

def get_update_today(num,types):
    """
	同一天内更新哦数据
    """
    data = db[types].find_one({'time':today})
    if data:
        datas = data[0]['datas'][num:]
    else:
        return [],num
	return datas,len(datas)
    
def get_udate_yestoday(t,num,types):
    """
	跨天更新昨天加今天
	@params t:时间
	@params num:当时更新条数
	@return :datas,本次更新条数
	"""
    data = db[types].find_one({'time':t})
    if not data:
        return [],num
    datas = data[0]['datas'][num:]
	#昨天与今天数据一起
	today_datas,today_num = get_update(0,types)
	if today_datas:
        datas += today_datas
		return datas,today_num
	return datas,len(datas)


def set_ver(types):
    con = pymongo.Connection()
    db = con.datas
    db2 = con.datas_key
    db_ver = con.datas_ver
    today = str(datetime.date.today())
    ver_config = db_ver[types].find_one({'type':types})
    t = str(datetime.date.today())
    if ver_config:
        ver = ver_config['ver'].split("+")[1]
        ver_config.update({'type':types},{'$set':{'ver': "%s+%d" % (t,ver+1)}})
    else:
        db_ver[types].insert({'type':types,'ver':"%s+%d" % (t,0)})
	print 'set_ver',db_ver[types].find_one({'type':types})

def get_ver(types):
    ver = db_ver[types].find_one({'type':types})
    if ver:
        ver = ver[0]['ver']
    else:
        ver = "%s+%d" % (str(datetime.date.today()),0)
    return ver


if __name__ == "__main__":
    for i in range(1,1000000):
        save('fine',{'data1':[{'aa':'a1'},{'bb':'b1'},{'cc':'c1'}],'count':i})


    for j in range(5555,5556):
        datas,next_num = get(num=j,types='fine')
        print next_num
        print datas
