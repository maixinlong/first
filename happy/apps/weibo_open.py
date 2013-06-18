#! /usr/bin/env python
#coding=utf-8
import sys
import urllib
import urllib2
from weibo import APIClient
from cache.mccache import MemcacheClient
import redis

# weibo api访问配置
APP_KEY = '3348709186'      # app key
APP_SECRET = '03dcd649f6420307849aa1b5bfc6fa78'   # app secret
#callback url 授权回调页,与OAuth2.0 授权设置的一致
CALLBACK_URL = 'https://api.weibo.com/oauth2/default.html' 
USERID = '346330910@qq.com'       # 微博用户名                     
USERPASSWD = 'mxl@sina.com'   # 用户密码
AUTH_URL = 'https://api.weibo.com/oauth2/authorize'
client = APIClient(app_key=APP_KEY, app_secret=APP_SECRET,redirect_uri=CALLBACK_URL)

mc = MemcacheClient({"servers":"localhost:11211","default_timeout":0})
rd = redis.Redis(host='localhost', port=6379, db=1)

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
    

def get_weibo(msg='冷笑话精选'):
    """
    常用参数：
    since_id 若指定此参数，则返回ID比since_id大的微博（即比since_id时间晚的微博），默认为0。 
    count 单页返回的记录条数，最大不超过100，默认为20。 
    """
    client = weibo_client()
    #返回json格式
    k = client.statuses.user_timeline.get(screen_name="时尚经典语录吖",count=200)
    weibo = dict(k)    
    print weibo['statuses'][0]['text']
    print weibo['statuses'][0]['id']
    print weibo['statuses'][1]['id']
    print weibo['statuses'][len(weibo['statuses'])-1]['created_at']
    
    print len(weibo['statuses'])
    #k = client.search.suggestions.users.get(q="时尚",count=100)
    
    return
    b = []
    for item in k :
        b.append( item['screen_name'])
    mc.set('weibo_type_shishang',b)
    #print weibo['statuses'][0]['id']
    
    return
    for i in range(1,15):
        #微博内容
        print weibo['statuses'][i]['text']
        #转发数
        print weibo['statuses'][i]['reposts_count']  
        #评论数 
        print weibo['statuses'][i]['comments_count']
        #中等尺寸图片地址，没有时不返回此字段 
        if weibo['statuses'][i].get('bmiddle_pic'):
            print weibo['statuses'][i]['bmiddle_pic']
        #缩略图片地址，没有时不返回此字段 
        if weibo['statuses'][i].get('thumbnail_pic'):
            print weibo['statuses'][i]['thumbnail_pic']
        
        
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
    
    
if __name__ == '__main__':
    msg = sys.argv[1:]
    if True:
        get_weibo(msg)
    else:
        print "请输入内容..."