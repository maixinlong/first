# -*- coding: utf-8 -*-
#/usr/bin/env python

__version__ = '1.0'
__author__ = 'http://weibo.com/wtmmac'

'''
Demo for sinaweibopy
主要实现token自动生成及更新
适合于后端服务相关应用
'''

# api from:http://michaelliao.github.com/sinaweibopy/
from weibo import APIClient

import sys, os, urllib, urllib2
from http_helper import *
from retry import *
try:
    import json
except ImportError:
    import simplejson as json

# setting sys encoding to utf-8
default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)

# weibo api访问配置
APP_KEY = '3348709186'      # app key
APP_SECRET = '03dcd649f6420307849aa1b5bfc6fa78'   # app secret
CALLBACK_URL = 'https://api.weibo.com/oauth2/default.html' # callback url 授权回调页,与OAuth2.0 授权设置的一致
USERID = '346330910@qq.com'       # 微博用户名                     
USERPASSWD = 'mxl@sina.com'   # 用户密码
AUTH_URL = 'https://api.weibo.com/oauth2/authorize'

# token file path
save_access_token_file  = 'access_token.txt'
file_path = os.path.dirname(__file__) + os.path.sep
access_token_file_path = file_path + save_access_token_file

client = APIClient(app_key=APP_KEY, app_secret=APP_SECRET, redirect_uri=CALLBACK_URL)

def make_access_token():
    '''请求access token'''
    params = urllib.urlencode(
        {'action':'submit','withOfficalFlag':'0','ticket':'','isLoginSina':'0', \
        'response_type':'code', \
        'regCallback':'', \
        'redirect_uri':CALLBACK_URL, \
        'client_id':APP_KEY, \
        'state':'', \
        'from':'', \
        'userId':USERID, \
        'passwd':USERPASSWD, \
        })

    url = client.get_authorize_url()
    
    #指定header
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; rv:11.0) Gecko/20100101 Firefox/11.0",
               "Host": "api.weibo.com",
               "Referer": url
             }

    headers = {'Referer':url}
    request = urllib2.Request(url = AUTH_URL,data = params,headers = headers)
    code_url = urllib2.urlopen(request)
    code = code_url.geturl().split('code=')[1]
    print 'code:',code

    #得到token
    token = client.request_access_token(code)
    save_access_token(token)

def save_access_token(token):
    '''将access token保存到本地'''
    f = open(access_token_file_path, 'w')
    f.write(token['access_token']+' ' + str(token['expires_in']))
    f.close()

#@retry(1)
def apply_access_token():
    '''从本地读取及设置access token'''
    try:
        token = open(access_token_file_path, 'r').read().split()
        if len(token) != 2:
            make_access_token()
            return False
        # 过期验证
        access_token, expires_in = token
        try:
            client.set_access_token(access_token, expires_in)
        except StandardError, e:
            if hasattr(e, 'error'): 
                if e.error == 'expired_token':
                    # token过期重新生成
                    make_access_token()
            else:
                pass
    except:
        make_access_token()
    
    return False

if __name__ == "__main__":
    apply_access_token()
    
    # 以下为访问微博api的应用逻辑
    # 以接口访问状态为例
    status = client.get.account__rate_limit_status()
    print json.dumps(status)