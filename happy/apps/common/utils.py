# encoding: utf-8
""" utils.py
定义一些手机开发相关的共同的代码
Copyright (c) 2011 Rekoo Media. All rights reserved.
"""
import time
import datetime
import os
import re
import random
import sys
import traceback
import urllib
import uamobile

from django.utils.encoding import smart_unicode
from oscontainer import os_data
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.conf import settings
from rklib.utils.cache import cache

from apps.config import game_config

def print_err():
    sys.stderr.write('==' * 30 + os.linesep)
    sys.stderr.write('err time: ' + str(datetime.datetime.now()) + os.linesep)
    sys.stderr.write('--' * 30 + os.linesep)
    traceback.print_exc(file=sys.stderr)
    sys.stderr.write('==' * 30 + os.linesep)

def resume_time_str(dis_time):
    time_str = ''
    second = dis_time.seconds
    day = dis_time.days
    hour = day * 24 + second / 3600
    minute = (second % 3600) / 60
    if not minute:
        minute = 1

    if hour:
        time_str += '%d時間' % hour

    if minute:
        time_str += '%d分' % minute
    return time_str

def paginator(object_list, number, per_page=5):
    """Django分页类Paginator的简单包装，保留Paginator类原有的属性及方法
    Args:
        object_list: A list, tuple, Django QuerySet, or other sliceable object with a count() or __len__() method.
        number: The 1-based page number for this page.
        per_page: The maximum number of items to include on a page, not including orphans (see the orphans optional argument below).
    
    Returns:
        page: a Django Page object with the given 1-based index.
    """
    paginator = Paginator(object_list, per_page)

    try:
        number = int(number)
    except ValueError:
        number = 1

    try:
        page = paginator.page(number)
    except (EmptyPage, InvalidPage):
        page = paginator.page(paginator.num_pages)

    return page

def get_list_page(l, size, page, desc_dict={}):
    """ 分页处理
    context['item_list'] = utils.get_list_page(item_list, 10, page, context)
    参数描述:
        l:欲分页的list
        size:分页大小
        page：返回第几页
        desc_dict:储存分页参数的变量 一般可为context
    返回说明:当前分页的元素列表
    """
    paginator = Paginator(l, size)
    try:
        current_paginator = paginator.page(page)
    except (EmptyPage, InvalidPage):
        current_paginator = paginator.page(paginator.num_pages)

    desc_dict['pages'] = {}
    if current_paginator.has_next():
        desc_dict['pages']["next_page"] = current_paginator.next_page_number()
        desc_dict['pages']["has_next"] = True
    if current_paginator.has_previous():
        desc_dict['pages']["pre_page"] = current_paginator.previous_page_number()
        desc_dict['pages']["has_pre"] = True
    desc_dict['pages']['page'] = page
    desc_dict['pages']['page_nums'] = paginator.num_pages
    return current_paginator.object_list

def make_mobile_url(request, url, pure=False, redirectFlg=False):
    """生成页面的url
    """
    params = ''
    params_link_char = ''
    if request:
        params = 'signed=1&guid=ON&' + settings.SESSION_COOKIE_NAME + '='\
                 + request.session.session_key + '&t=' +\
                 str(time.mktime(datetime.datetime.now().timetuple()))
    if params:
        params_link_char = '&' if '?' in url else '?'

    #不添加任何参数直接跳转
    if pure:
        mobile_url = settings.BASE_URL + url
    else:
        mobile_url = settings.BASE_URL + url + params_link_char + params

    if settings.LOCAL_DEBUG:
        return mobile_url

    if not redirectFlg:
        if request.agent_device['device'].is_smartphone:
            app_url = os_data['app_url_sp'] % {"app_id": settings.APP_ID}
        else:
            app_url = os_data['app_url'] % {"app_id": settings.APP_ID}
        mobile_url = urllib.quote_plus(mobile_url)
        mobile_url = '%s/?guid=ON&url=%s' % (app_url, mobile_url )
        #--------------end----------------------
    return mobile_url

def mobile_redirect(request, url, pure=False):
    """ 输出302跳转"""

    #--------------start----------------------
    #GREEの場合、リダイレクトURLの構造がmixiと異なるため、フラグを追加する by hao.sun
    #return HttpResponseRedirect(make_media_url(request, url))
    return HttpResponseRedirect(make_mobile_url(request, url, pure=pure, redirectFlg=True))
    #--------------end----------------------   

def make_media_url(request, url, redirectFlg=False):
    """生成flash
    """
    params = ''
    params_link_char = ''
    if request:
        params = 'signed=1&guid=ON&' + settings.SESSION_COOKIE_NAME + '='\
                 + request.session.session_key + '&t=' +\
                 str(time.mktime(datetime.datetime.now().timetuple()))
    if params:
        params_link_char = '&' if '?' in url else '?'

    mobile_url = settings.BASE_URL + url + params_link_char + params
    wapper_url = settings.BASE_URL + '/flashwrapper/' + params_link_char + params

    if settings.LOCAL_DEBUG:
        return mobile_url

    if request.agent_device['device'].is_smartphone:
        mobile_url = urllib.quote_plus(mobile_url)
        mobile_url = '%s&flashurl=%s' % (wapper_url, mobile_url)
        return mobile_url

    if not redirectFlg or os_data['name'] == 'mixi':
        app_url = os_data['media_url'] % {"app_id": settings.APP_ID}
        mobile_url = urllib.quote_plus(mobile_url)
        mobile_url = '%s/?guid=ON&url=%s' % (app_url, mobile_url)
        #--------------end----------------------

    return mobile_url

def mobile_media_redirect(request, url):
    """ 输出素材的地址如flash输出302跳转"""
    return HttpResponseRedirect(make_media_url(request, url, redirectFlg=True))

def create_gen_id():
    """根据时间生成一个id """
    gen_id = str(datetime.datetime.now()).replace(' ', '').replace('-', '').replace(':', '').replace('.', '')

    return gen_id

#def get_msg(category_key, msg_key):
#    """获取提示信息 """
#    return msg_config.get(category_key,{}).get(msg_key,'')

def get_today_str():
    """取得今天的日期字符串"""
    return datetime.date.today().strftime('%Y-%m-%d')

def utc_to_tz(utc_dt_str, utc_fmt='%Y-%m-%dT%H:%M:%SZ', tz=None):
    """
        将UTC时区的时间转换为当前时区的时间
        当前时区取django settings.py 中设置的时区
        如：在settings.py文件中的设置
        TIME_ZONE = 'Asia/Tokyo'
        
        PARAMS:
            * utc_dt_str - utc时区时间，字符串类型。如：2010-01-14T07:00:20Z
            * utc_fmt - utc时区时间格式。如：%Y-%m-%dT%H:%M:%SZ
            * tz - 当前时区，如：Asia/Tokyo
            
        RETURNS: tz_dt
    """
    if tz is None:
        tz = os.environ['TZ']

    utc_fmt_dt = datetime.datetime.strptime(utc_dt_str, utc_fmt)
    utc_dt = datetime.datetime(utc_fmt_dt.year, utc_fmt_dt.month, utc_fmt_dt.day, utc_fmt_dt.hour, utc_fmt_dt.minute,
        utc_fmt_dt.second, tzinfo=pytz.utc)
    tz_dt = utc_dt.astimezone(pytz.timezone(tz))

    return tz_dt

def get_index_by_random(weight_list):
    """ 根据权重数组中设定的各权重值随机返回该权重数组的下标
        args:
            * weight_list - 权重数组
            
        returns: int 权重数组的下标
    """

    total_weight = 0
    weight_list_temp = []

    #计算总权重
    for weight in weight_list:
        total_weight = total_weight + weight
        weight_list_temp.append(total_weight)

    #在总权重数中产生随机数
    random_value = random.randint(1, total_weight)

    #根据产生的随机数判断权重数组的下标
    list_index = 0
    for weight_temp in weight_list_temp:
        if random_value <= weight_temp:
            break
        list_index += 1

    return list_index

def get_item_by_random(item_list, weight_list=[]):
    """ 根据权重数组中设定的各权重值随机返回item列表中的item
        args:
            * item_list - item数组
            * weight_list - 权重数组
            
        returns: 随机指定的item
    """

    if (item_list is None) or (len(item_list) == 0):
        return None

    if (weight_list is None) or (len(weight_list) == 0):
        random_index = random.randint(0, len(item_list) - 1)
    else:
        if len(item_list) != len(weight_list):
            return None
        else:
            random_index = get_index_by_random(weight_list)

    return item_list[random_index]

def get_item_by_random_simple(item_weight_list):
    """ 根据权重数组中设定的各权重值随机返回item列表中的item
        args:
            * item_weight_list - item,权重数组
            
        returns: 随机指定的item
    """

    if (item_weight_list is None) or (len(item_weight_list) == 0):
        return None

    item_list = []
    weight_list = []

    for item_weight in item_weight_list:
        item_list.append(item_weight[0])
        weight_list.append(item_weight[1])

    return get_item_by_random(item_list, weight_list)

def cul_processbar_width(total_width, total_value, cur_value):

    cur_value_width = int(round(((cur_value * 1.0) / total_value) * total_width))
    used_value_width = total_width - cur_value_width
    return cur_value_width, used_value_width

def cul_to_damage(self, self_at, side_df, at_rate, df_rate):
    to_damage = int((self_at * at_rate) - (side_df * df_rate))
    if to_damage < 0:
        to_damage = 0

    return to_damage

def cul_from_damage(self, self_df, side_at, at_rate, df_rate):
    from_damage = int((side_at * at_rate) - (self_df * df_rate))
    if from_damage < 0:
        from_damage = 0

    return from_damage

def is_happen(rate, unit=100):
    """根据概率判断事件是否发生
    args:
        rate:概率。可以为小数，也可以为整数。为整数时，总和为unit参数
        unit:当rate为整数时，表示总和
    return:
        bool,是否发生
    """
    happend = False
    if isinstance(rate, int):
        random_value = random.randint(1, unit)
        if rate >= random_value:
            happend = True
    elif isinstance(rate, float):
        random_value = random.random()
        if rate >= random_value:
            happend = True
    return happend

def agent_check(request):
    """
     agent_check for japan mobile
    """
    useragent = request.META.get("HTTP_USER_AGENT")
    DOCOMO_RE = re.compile(r'^DoCoMo/\d\.\d[ /]')
    SOFTBANK_RE = re.compile(r'^(?:(?:SoftBank|Vodafone|J-PHONE)/\d\.\d|MOT-)')
    EZWEB_RE = re.compile(r'^(?:KDDI-[A-Z]+\d+[A-Z]? )?UP\.Browser\/')
    WILLCOM_RE = re.compile(
        r'^Mozilla/3\.0\((?:DDIPOCKET|WILLCOM);|^Mozilla/4\.0 \(compatible; MSIE (?:6\.0|4\.01); Windows CE; SHARP/WS\d+SH; PPC; \d+x\d+\)')
    if DOCOMO_RE.match(useragent):
        return "docomo"  #docomo机型
    elif EZWEB_RE.match(useragent):
        return "au"   #au 、kddi 、 ezweb 机型
    elif SOFTBANK_RE.match(useragent):
        return "softbank" #软银、 sb 、softbank、机型
    elif WILLCOM_RE.match(useragent):
        return "willcom" #willcom 机型
    else:
        return "pc"     #非手机

def in_ua_black_list(request):
    """检查手机ua是否在黑名单里
    """
    conf = game_config.sys_config.get('ua_black_list',{})
    flag = False
    ua = uamobile.detect(request.META)
    if request.agent_device['device'].is_smartphone:
        if request.agent_device['device'].is_ios:
            return True
        return False
    #docomo
    elif ua.is_docomo():
        if ua.model in conf.get('docomo',[]):
            flag = True
    #au
    elif ua.is_ezweb():
        if ua.model in conf.get('au',[]):
            flag = True
    #softbank
    elif ua.is_softbank():
        if ua.model in conf.get('softbank',[]):
            flag = True
    #willcom机型全部屏蔽
    elif ua.is_willcom():
        flag = True
    else:
        userAgent = str(request.META.get("HTTP_USER_AGENT")).lower()
        match = re.match("(.*)"+"mozilla"+"(.*)", userAgent)
        if not match:
            match = re.match("(.*)"+"willcom"+"(.*)", userAgent)
        if match:
            flag = True
    return flag

def get_pre_last(item, items):
    """获取上一个item和下一个item """
    try:
        index = items.index(item)
    except:
        return None, None
    pre = None
    last = None
    if 0 < index:
        pre = items[index - 1]
    if index < (len(items) - 1):
        last = items[index + 1]
    return pre, last

def sys_control_time():
    #防止交叉引用
    from apps.config import game_config

    sys_c = game_config.sys_config
    now = datetime.datetime.now()
    if sys_c.get("day")[0] <= now.hour <= sys_c.get("day")[1]:
        return "day"
    else:
        return "night"

def update_active_user(uid):
    """更新活跃用户列表"""
    user_list = cache.get('active_user_list', [])
    if uid not in user_list:
        user_list.insert(0, uid)

    if len(user_list) > 1000:
        user_list = user_list[:1000]

    cache.set('active_user_list', user_list)

def get_active_users():
    """获取活跃用户"""
    return cache.get('active_user_list', [])

def get_active_strangers(rk_user):
    """获取当前活跃陌生人的列表"""
    l = get_active_users()
    return [uid for uid in l if uid not in rk_user.friend.game_friends] 

def get_week(d_time):
    """
    d_time:datetime
    """
    week_str = ''
    week = d_time.strftime("%w")
    if week == '1':
        week_str = '月'
    elif week == '2':
        week_str = '火'
    elif week == '3':
        week_str = '水'
    elif week == '4':
        week_str = '木'
    elif week == '5':
        week_str = '金'
    elif week == '6':
        week_str = '土'
    elif week == '0':
        week_str = '日'
        
    return week_str
