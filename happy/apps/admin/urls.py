#-*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('apps.admin.views.admin',
    (r'^$', 'index'),
    (r'^login/$', 'login'),
    (r'^sign/$', 'sign'),
    (r'^left/$', 'left'),
    (r'^main/$', 'main'),
    (r'^middle/$', 'middle'),
    
    
    )

#微博用户统计数据
urlpatterns += patterns('apps.admin.views.weibo_info',
    (r'^weibo_users/$', 'weibo_users'),
    (r'^weibo_info/$', 'weibo_info'),
    
    )
