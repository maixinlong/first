#!/usr/bin/env python
#-*- coding: utf-8 -*-
import redis
import json
import pickle
import datetime

from apps.common.http_util import render,render_text

rd = redis.Redis(host='localhost', port=6379, db=1)

def get_content1111111(request):
    page = int(request.GET.get('page',1))
    types = request.GET.get('type',0)
    
    datas = rd.get('liuxin_test')
    datas = pickle.loads(datas)
    datas = datas[:page*20]
    
    if types == "dynamic":
        datas = rd.get('liuxin_gif')
        datas = pickle.loads(datas)
        datas = datas[:page*20]
        datas.sort(key=lambda a:(a.get('file_size')), reverse=False)
    
    
    
    #data = json.dumps(,sort_keys=True,indent=4, separators=(',', ': '))
    data = json.JSONEncoder().encode( {'num':20,'list':datas} )
    print data
    return render_text(data)
    

def update_content(request):
    types = request.GET.get('type','fine')
    last_datas = []
    new_datas = []
    if types not in ['dynamic','fine']:
        types = 'fine'
    new_datas = rd.get(types)
    #新旧数据比对、新数据与老数据是否累计？
    #

    datas = pickle.loads(new_datas)[:20]
    if not datas:
        datas = last_datas
    last_id = datas[-1]['id']
    data = json.JSONEncoder().encode( {'last_id':last_id,'count':20,'list':datas,'update_time':'2013-06-27'})
    return render_text(data)


def get_content(request):
    types = request.GET.get('type','fine')
    #last_id 得初次加载时传上去
    last_id = request.GET.get('last_id',0)
    
    if types not in ['fine','dynamic']:
        types = 'fine'
    datas = rd.get(types)
    datas = pickle.loads(datas)
    #比较上一条位置，往后接着取
    for i in datas:
        if i['id'] == last_id:
            index = datas.index(i)
            datas = datas[:index+20]
            break
    last_id = datas[-1]['id']
    data = json.JSONEncoder().encode( {'last_id':last_id,'list':datas} )
    print data
    return render_text(data)
