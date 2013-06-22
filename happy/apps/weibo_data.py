#! /usr/bin/env python
#coding=utf-8
from cache.mccache import MemcacheClient
from models.weibo_user import WeiboUser
from models.content import Content
from models.weibo import Weibo
import urllib, cStringIO
from PIL import Image
import datetime
import get_robot
import time
import redis
import sys
import urllib
import urllib2
import re

#拿到微博对象
client = get_robot.weibo
weibo_user = WeiboUser.get()

#初始化2个存储引擎
mc = MemcacheClient({"servers":"localhost:11211","default_timeout":0})
rd = redis.Redis(host='localhost', port=6379, db=1)

time_dict = {"Jan":1,"Feb":2,"Mar":3,"Apr":4,"May":5,"Jun":6,"Jul":7,"Aug":8,"Sep":9,"Oct":10,"Nov":11,"Dec":12,}

"""
a =['2013-5-1', '2013-5-2', '2013-5-3', '2013-5-4', '2013-5-5', '2013-5-6', '2013-5-7', '2013-5-8', '2013-5-9', '2013-5-10', '2013-5-11', '2013-5-12', '2013-5-13', '2013-5-14', '2013-5-15', '2013-5-16', '2013-5-17', '2013-5-18', '2013-5-19', '2013-5-20', '2013-5-21', '2013-5-22', '2013-5-23', '2013-5-24', '2013-5-25', '2013-5-26', '2013-5-27', '2013-5-28', '2013-5-29', '2013-5-30', '2013-5-31', '2013-6-01', '2013-6-02', '2013-6-03', '2013-6-04', '2013-6-05', '2013-6-06', '2013-6-07', '2013-6-08', '2013-6-09', '2013-6-10', '2013-6-11', '2013-6-12', '2013-6-13', '2013-6-14', '2013-6-15', '2013-6-16', '2013-6-17', '2013-6-18', '2013-6-19', '2013-6-20', '2013-6-21']
import weibo_data
for item in a:
    weibo_data.stat_user(item)
"""

"""
1.批量添加大类别 weibo_data.search_users("搞笑")
2.批量获取大类别微博用户信息 weibo_data.search_user("搞笑")
3.抓取内容这些微博用户 weibo_data.get_contents("搞笑")
4.统计这些微博用户的数据stat_user(时间)
"""
def search_users(keywords,count=100,debug=False):
    """
    搜索关键字查询类别
    默认返回100个用户
    debug:调试模式不保存 只输出
    """
    users = []
    w_user = WeiboUser.get()
    result = client.search.suggestions.users.get(q=keywords,count=count)
    for item in result:
        w_user.userids[item['uid']] = item['screen_name']
        users.append(item['uid'])
        if debug:
            print item['screen_name'],item['uid']
    w_user.users[keywords] = users
    if not debug:
        w_user.put()
        print "ok"

def search_user(keywords,debug=False,force_update=False):
    """
    根据类别更新微博用户的常用信息
    如果keywords没有会出错
    应该先执行search_users查询结果
    debug:调试模式只输出 不保存数据
    force_update:强制更新所有微博(以为新浪对开发者有请求次数限制 尽量少做没用的请求)
    """
    if keywords not in weibo_user.users:
        weibo_user.users[keywords] = []
        weibo_user.put()
        
    for item in weibo_user.users[keywords]:
        #如果已经存在这个用户了 就不在更新数据 除非强制刷新模式
        wb = Weibo.get(item)
        if wb and not force_update:
            continue
        
        #item:微博id
        result = client.users.show.get(uid=item)
        user_info = dict(result)
        if not wb:
            wb = Weibo._install(item)
        
        wb.screen_name = user_info['screen_name']
        wb.statuses_count = user_info['statuses_count']
        wb.followers_count = user_info['followers_count']
        wb.profile_image_url = user_info['profile_image_url']
        wb.avatar_large = user_info['avatar_large']
        if debug:
            print item
            print "  ","statuses_count",user_info['statuses_count']
            print "  ","followers_count",user_info['followers_count']
            print "  ","profile_image_url",user_info['profile_image_url']
            print "  ","avatar_large",user_info['avatar_large']
            continue
        wb.put()
        print "ok"

def get_contents(weibo_type,debug=False,force_update=False):
    """
    批量抓取类别的所有用户数据
    """
    slen = len(weibo_user.users[weibo_type])
    for item in weibo_user.users[weibo_type]:
        slen-=1
        print slen
        get_content(weibo_type,item,debug=debug,force_update=force_update)
        
def stat_user(search_time=None,force_update=False):
    """
    统计用户信息
    """
    if not search_time:
        search_time = datetime.datetime.now()
        search_time = "%s-%s-%s"%(now_time.year,now_time.month,now_time.day)
    content = Content.get(search_time)
    if not content:
        return
    #遍历所有用户
    for types,ids in content.weibo.iteritems():
        for id,context in ids.iteritems():
            user = Weibo.get(id)
            #如果还没有今天的统计就统计一下
            if not user.stat_info.get(search_time) or force_update:
                create_at = []
                for tmp_content in context:
                    if not tmp_content.get('created_at'):continue
                    create_at.append(tmp_content['created_at'].split(' ')[3].split(':')[0])
                user.stat_info[search_time] = {}
                user.stat_info[search_time] = {'send_count':len(context),'create_at':create_at}
                #print ,create_atuser.stat_info[search_time]
                user.put()
        
def get_content(weibo_type,user_id,debug=False,count=200,force_update=False):
    """
    抓取微博内容
    weibo_type:微博类型  注意需要是已经存在的类别
    user_id:微博的id 注意这里不是微博名字 是微博id 
    debug:调试模式 不插入数据库
    force_update:强制更新  删除所有 重新获取
    """
    content_dict = {}
    #ty:时尚 美图 旅游 搞笑.....
    #用户id
    result = client.statuses.user_timeline.get(uid=user_id,count=count)
    contents = dict(result)
    #遍历所有发的帖子 前100条
    for s_item in contents['statuses']:
        
        #可能是转帖 所以需要再取一次
        if not s_item.get('original_pic'):
            if s_item.get('retweeted_status',{}).get('original_pic'):
                s_item['original_pic'] = s_item['retweeted_status']['original_pic']
            else:
                #如果没有图片 就pass掉
                continue
            
        #filter列表包含这些内容不保存 可能是广告数据
        if "http://" in s_item['text'] or "包邮" in s_item['text']\
         or "www." in s_item['text'] or re.findall('[0-9]元',s_item['text'])\
         or s_item['text'].count(" ★") >= 3 or s_item['text'].count("（") >= 3\
         or s_item['text'].count("：") > 5 or s_item['text'].count("【") > 2\
         or s_item['text'].count("、") > 5 or '@' in s_item['text']\
         or '#' in s_item['text']:
            continue
        #不筛选gif图片
        if '.gif' in s_item.get('original_pic',''):
            continue
        #判断字数大于200的话过滤
#        if len(s_item['text'].decode('utf-8') >= 200):
#            continue
        
#        #计算图片的大小
#        if s_item.get('original_pic'):
#            response = urllib.urlopen(url=s_item['original_pic'])
#            img_data = response.read()
#            io = cStringIO.StringIO(img_data)
#            s_item['width'],s_item['height'] = Image.open(io).size
            
        #格式化时间  按照时间分开存放内容
        created_at = s_item['created_at'].split(' ')
        time_str = created_at[len(created_at)-1] + "-" + str(time_dict[created_at[1]]) + '-' + created_at[2]
        if time_str not in content_dict:
            content_dict[time_str] = {}
            
        #[时间][搞笑][周杰伦的微博的id]  注意是id哦~
        if user_id not in content_dict[time_str]:
            content_dict[time_str][user_id] = []
        need_data = {
                     'id':s_item['id'],
                     'screen_name':weibo_user.userids[int(user_id)],
                     'type':weibo_type,
                     'text':s_item['text'],
                     'bmiddle_pic':s_item.get('bmiddle_pic'),
                     'original_pic':s_item.get('original_pic'),
                     'thumbnail_pic':s_item.get('thumbnail_pic'),
                     'reposts_count':s_item.get('reposts_count'),
                     'comments_count':s_item.get('comments_count'),
                     'attitudes_count':s_item.get('attitudes_count'),
                     'mlevel':s_item.get('mlevel'),
                     'width':s_item.get('width'),
                     'height':s_item.get('height'),
                     'text_size':len(s_item['text'].decode('utf-8')),
                     
                     'avatar_large':s_item.get('user',{}).get('avatar_large'),
                     'profile_image_url':s_item.get('user',{}).get('profile_image_url'),
                     
                     }
        #[时间][用户id] = [微博,微博,微博]
        content_dict[time_str][user_id].append(need_data)
        
    #按照时间分开存储 k:时间 :{用户id:[]}
    for k,v in content_dict.iteritems():
        cont_obj = Content.get(k)
        if not cont_obj:
            cont_obj = Content._install(k)
        #新添加类别 
        if weibo_type not in cont_obj.weibo:
            cont_obj.weibo[weibo_type] = v
        else:
            #有可能内容已经存在 u_id:用户id item_value:帖子集合[]
            for u_id,item_value in v.iteritems():
                #如果没用该用户的信息 创建
                if u_id not in cont_obj.weibo[weibo_type] or force_update:
                    cont_obj.weibo[weibo_type][u_id] = item_value
                else:
                    
                #如果有该用户信息 需要判断是否有重复内容
                    now_ids = [va['id'] for va in cont_obj.weibo[weibo_type][u_id]]
                    for cont in item_value:
                        if cont['id'] not in now_ids:
                            cont_obj.weibo[weibo_type][u_id].append(cont)
        if not debug:
            a = time.time()
            cont_obj.put()
            print 'result',time.time()-a
        
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
    
