#!/usr/bin/env python
#-*- coding: utf-8 -*-
from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

#后台管理
urlpatterns = patterns('',
    url(r'^admin/',include('apps.admin.urls'),name = "admin"),
) 

