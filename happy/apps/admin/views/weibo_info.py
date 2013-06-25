#-*- coding: utf-8 -*-from apps.common.http_util import render,redirectfrom django.conf import settingsfrom cache.mccache import MemcacheClientfrom models.weibo_user import WeiboUserfrom models.weibo import Weibofrom models.content import Contentimport redisimport pickleimport calendarimport datetime#从5月12日开始抓数据#从5月开始#当月天数base_time = datetime.datetime(2013, 5, 1)month_count = calendar.monthrange(2013,5)[1]weibo_info_list = [              ('/admin/weibo_info/',"帖子排列"),              ('/admin/weibo_users/',"用户信息统计"),              ]weibo_infos = {'weibo_name':"微博名称",               'followers_count':"粉丝数",               'everyday_weibo_count':"每日微博数",               'everyday_comment':"每日评论",               'everyday_transmit':"每日转发",               'everyday_praise':"每日赞",               'everyday_participate':"平均用户参与度",               'everyday_sendtime':"平均发微博时间",               'everyday_commenttime':"用户平均评论时间",               }sort_rule = {             "article_count":("帖子数","方法名"),             "attitudes_count":("赞","方法名"),             "reposts_count":("转发","方法名"),             "comments_count":("评论数","方法名"),             }mc = MemcacheClient({"servers":"localhost:11211","default_timeout":0})rd = redis.Redis(host='localhost', port=6379, db=1)weibo_user = WeiboUser.get()def weibo_users(request):    """    微博用户统计    """    #查询时间    #查询类别    print "0000"*40    now_time = datetime.datetime.now()    now_time = "%s-%s-%s"%(now_time.year,now_time.month,now_time.day)    search_time = request.GET.get('search_time',now_time)    search_type = request.GET.get('search_type','时尚').encode('utf-8')    sort = request.GET.get('sort','comments_count')    data = {'url_list':weibo_info_list,            'time_list':[],            'user_list':[],            "search_time":search_time,            "search_type":search_type,            "sort_rule":sort_rule,            'types':weibo_user.users.keys(),            }        #显示日期列表 比较傻瓜 先这么写着吧    for item in xrange(1,month_count+1):        time_str = "2013-5-%s"%str(item)        if Content.get(time_str):            data['time_list'].append(("5月%s日"%str(item),time_str))    for item in xrange(1,datetime.datetime.today().day+1):        if item <= 9:            time_str = "2013-6-0%s"%str(item)        else:            time_str = "2013-6-%s"%str(item)        if Content.get(time_str):             data['time_list'].append(("6月%s日"%str(item),time_str))                 #数据统计    weibo_data = weibo_user.users[search_type]    #item:用户id 遍历用户看是否做过统计    for id in weibo_data:        user = Weibo.get(id)        stat = user.stat_info.get(search_time)        if not stat : continue        create_at = list(set(stat['create_at']))        print stat        create_at.sort()        stat_data = {                     "user_name":weibo_user.userids[id],                     "send_count":stat['send_count'],                     "create_at":"点,".join(create_at) + "," ,                     "followers_count":user.followers_count,                     }        data['user_list'].append(stat_data)            print "11111"*40    return render("admin/weibo_users.html", data, request)def weibo_info(request):    """    微博信息    """    #查找时间 默认是今天    #查找内容类别    #排序规则    search_time = request.GET.get('search_time',datetime.datetime.now().strftime('%Y-%-m-%-d'))    search_type = request.GET.get('search_type','搞笑').encode('utf-8')    sort = request.GET.get('sort','comments_count')        data = {'url_list':weibo_info_list,            'weibo_infos':weibo_infos,            'users':[],            'types':weibo_user.users.keys(),            'time_list':[],            'sort_rule':sort_rule,            'contents':[],            'search_time':search_time,            'search_type':search_type,            'sort':sort,            }            #显示日期列表 比较傻瓜 先这么写着吧    for item in xrange(1,month_count+1):        time_str = "2013-5-%s"%str(item)        if Content.get(time_str):            data['time_list'].append(("5月%s日"%str(item),time_str))    for item in xrange(1,datetime.datetime.today().day+1):        if item <= 9:            time_str = "2013-6-0%s"%str(item)        else:            time_str = "2013-6-%s"%str(item)        if Content.get(time_str):             data['time_list'].append(("6月%s日"%str(item),time_str))    #取出时间内的内容 如果取不到 可能是还没有数据    contents = Content.get(search_time)    if contents and contents.weibo.get(search_type):        contents = contents.weibo[search_type]        for k in contents:            contents[k].sort(key=lambda a:(a.get(sort)), reverse=True)            #contents[k] = contents[k][:5]    data['contents'] = contents        return render("admin/weibo_info.html", data, request)