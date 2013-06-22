#! /usr/bin/env python
#coding=utf-8
import sys
import urllib
import urllib2
from weibo import APIClient
import datetime
import time

# weibo api访问配置
APP_KEY = '3348709186'      # app key
APP_SECRET = '03dcd649f6420307849aa1b5bfc6fa78'   # app secret
#callback url 授权回调页,与OAuth2.0 授权设置的一致
CALLBACK_URL = 'https://api.weibo.com/oauth2/default.html' 
USERID = '346330910@qq.com'       # 微博用户名                     
USERPASSWD = 'mxl@sina.com'   # 用户密码
AUTH_URL = 'https://api.weibo.com/oauth2/authorize'
client = APIClient(app_key=APP_KEY, app_secret=APP_SECRET,redirect_uri=CALLBACK_URL)


def weibo_client():
    """微博认证
    """
    code = __code()
    #print 'code:==',code
    r = client.request_access_token(code)
    access_token = r.access_token  # access token，e.g., abc123xyz456
    expires_in = r.expires_in      # token expires in
    #验证access_token
    client.set_access_token(access_token, expires_in)
    return client


def __code():
    """
    获取code
    """
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
    return code
    
def __test():
    """
    """
    client = weibo_client()
    #获取关注列表 3583325060832782
    myfriends = client.friendships.friends.get(uid=2601091753)
    print client.statuses.user_timeline.get()
    #发微博
    print client.statuses.update.post(status=u'test code 啊啊啊 再一次')
    #发带图片的微博
    print client.statuses.upload.post(status=u'test weibo with picture',pic=open('/Users/michael/test.png'))    
    
weibo = weibo_client()
