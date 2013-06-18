#-*- coding: utf8 -*-
from django.conf import settings
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import loader
from django.template import RequestContext
from django.utils.encoding import smart_str


def render(template_name, data=None, request=None, encoding='shift_jis'):
    t = loader.get_template(template_name)
    c = RequestContext(request, data)
    response = HttpResponse(t.render(c))
    
    return response


def render_html(template_name, data=None, request=None, encoding='utf-8'):
    """http response输出html
    类似django.shortcuts.render_to_response函数，在不能使用django默认的content type及charset时使用
    增加对http响应数据编码，设置content type及设置禁止使用缓存header
    
    Args:
        template_name: 模板名称
        data: 模板渲染数据
        request: HttpRequest实例，用于生成RequestContext实例
        encoding: HttpResponse及content_type编码格式
    
    Returns:
        response: HttpResponse 实例
    """
    context_instance = RequestContext(request) if request else None

    _content = loader.render_to_string(template_name, data, context_instance)

    response = HttpResponse(smart_str(_content, encoding=encoding, errors='ignore'),
                            content_type='application/xhtml+xml; charset=' + encoding)

    _set_no_cache_header(response)

    return response


def render_text(data, encoding='utf-8'):
    """http response输出文本
    
    Args:
        data: http响应文本数据
        encoding: HttpResponse及content_type编码格式
        
    Returns:
        response: HttpResponse 实例
    """
    response = HttpResponse(smart_str(data, encoding=encoding),
                            content_type='text/plain; charset=' + encoding)

    _set_no_cache_header(response)

    return response


def render_flash(data, encoding='utf-8'):
    """http response输出flash
    
    Args:
        data: http响应swf数据
        encoding: HttpResponse及content_type编码格式
        
    Returns:
        response: HttpResponse 实例
    """
    response = HttpResponse(data, content_type='application/x-shockwave-flash; charset=' + encoding)

    _set_no_cache_header(response)

    return response


def redirect(url, request=None):
    """手机版使用HttpResponseRedirect，避免手机端301提示
    
    Args:
        url: 不含host信息的url
        request: 当前请求的HttpRequest实例，用于获取session_key
    """
    sep = '&' if '?' in url else '?'
    url = url + sep + 'guid=on'

    if isinstance(request, HttpRequest):
        url = url + '&sessionid=' + request.session.session_key

    return HttpResponseRedirect(settings.BASE_URL + url)


def _set_no_cache_header(response):
    """为http response设置禁止使用缓存header
    
    Args:
        response: HttpResponse 实例
    """
    # HTTP 1.1 header
    # response['Cache-Control'] = 'no-cache, no-store'
    response['Cache-Control'] = 'private, no-cache, no-store, must-revalidate'
    # HTTP 1.0 header
    response['Pragma'] = 'no-cache'
    response['Expires'] = 0
