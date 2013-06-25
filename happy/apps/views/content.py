#!/usr/bin/env python
#-*- coding: utf-8 -*-
import redis
import json
import pickle

from apps.common.http_util import render,render_text

rd = redis.Redis(host='localhost', port=6379, db=1)

def get_content(request):
    page = int(request.GET.get('page',1))
    types = request.GET.get('type',0)
    
    datas = rd.get('liuxin_test')
    datas = pickle.loads(datas)
    datas = datas[:page*20]
    
    #data = json.dumps(,sort_keys=True,indent=4, separators=(',', ': '))
    data = json.JSONEncoder().encode( {'num':20,'list':datas} )
    print data
    return render_text(data)
    