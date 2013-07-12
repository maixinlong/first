#!/usr/bin/env python
#-*- coding: utf-8 -*-
import redis
import json
import pickle
import datetime
from apps.common.http_util import render,render_text
from apps.cache import mgdb_test as mgdb

DEBUG = False
rd = redis.Redis(host='localhost', port=6379, db=1)

def update_content(types,ver1,ver2):
    """
	往下拉更新数据
	"""
    #types = request.GET.get('type')
    #ver1 = request.GET.get('ver')
    ver2 = mgdb.get_ver(types)
    if types not in ['dynamic','fine','video']:
        return {}

    if ver1 == ver2:
        return {}
    #同一天更新、隔天、第一次加载
    if ver1.split("+")[0] == ver2.split("+")[0]:
        datas,update_num = mgdb.get_update_today(int(ver1.split("+")[1]),types)
    elif ver1.split("+")[0] == ver2.split("+")[0]:
        datas,update_num = mgdb.get_update_yesterday(ver1.split("+")[0],int(ver1.split("+")[1]),types)
    else:
        datas,update_num = mgdb.get_update_first(types)
  
    if update_num <= 0:
        return {}
    data = json.JSONEncoder().encode( {'ver':ver2,'count':update_num,'list':datas})
    return render_text(data)


def get_content(types,next_num):
    """
    往上拉读取旧数据
	"""
    #types = request.GET.get('type')
    #next_num = request.GET.get('next_num')

    datas,next_num = mgdb.get(next_num,types)
    if not datas:
        return {}
    datas = json.JSONEncoder().encode({'list':datas,'next_num':next_num})
    return render_text(data)


   




