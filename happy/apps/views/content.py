#!/usr/bin/env python
#-*- coding: utf-8 -*-
import redis
import json
import pickle
import datetime
from apps.common.http_util import render,render_text
from apps.cache import mgdb

DEBUG = False
rd = redis.Redis(host='localhost', port=6379, db=1)
ver2 = "001+15"

def update_content(request):
    """
	往下拉更新数据
	"""
    types = request.GET.get('type')
    ver1 = request.GET.get('ver')
    ver2 = mgdb.get_ver()
    if types not in ['dynamic','fine','video']:
        return {}

    if ver1 == ver2:
        return {}
    #同一天更新
    if ver1.split("+")[0] == ver2.split("+")[0]:
        datas = get_update(num,types)
	else:
        pass
	client_num = int(ver1)
	db_num = int(ver2)

	update_num = db_num - client_num
    if update_num <= 0:
        return {}
    #初次加载
    datas = mgdb.get(new=True)
    data = json.JSONEncoder().encode( {'ver':ver2,'count':update_num,'list':datas})
    return render_text(data)


def get_content(request):
    """
    往上拉读取旧数据
	"""
    types = request.GET.get('type')
    next_num = request.GET.get('num')

    datas,next_num = mgdb.get(num=next_num,types=types,new=False)
    ver = mgdb.get_ver()
    if not datas:
        return {}
    datas = json.JSONEncoder().encode({'list':datas,'ver':ver,'next_num':next_num})
    return render_text(data)


   




