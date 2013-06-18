#-*- coding: utf-8 -*-
"""
author:刘欣
memcache封装 客户端
"""
try:
    import memcache
    _pylibmc = False
except ImportError, e:
    import pylibmc as memcache
    _pylibmc = True
import pickle
    


def force_str(text, encoding="utf-8", errors='strict'):
    t_type = type(text)
    if t_type == str:
        return text
    elif t_type == unicode:
        return text.encode(encoding, errors)
    return str(text)

class MemcacheClient(object):
    
    def __init__(self,config):
        '''
        servers is a string like "121.199.7.23:11211;42.121.145.76:11211"
        '''
        servers = config['servers']
        default_timeout = config['default_timeout']
        self._current = memcache.Client(servers.split(';'))
        #如果用的是pylibmc库 添加配置
        if _pylibmc:
            self._current.behaviors['distribution'] = 'consistent'
            self._current.behaviors['tcp_nodelay'] = 1
        self.default_timeout = default_timeout
    
    def put_data(self, model_cls, pkey, data, create_new):
        #获取保存的key   类似 key|app.modles.friend|用户id
        cache_key = model_cls.generate_cache_key(pkey)
        #先dumps 转成二进制 序列化 1和2是二进制  HIGHEST_PROTOCOL:是2  快而剩空间
        val = pickle.dumps(data, pickle.HIGHEST_PROTOCOL)
        if create_new:
            flag = self._current.add(cache_key, val, self.default_timeout)
            if not flag:
                raise Exception('memcache client add failure, cache key: %s' % cache_key)
        else:
            flag = self._current.set(cache_key, val, self.default_timeout)
            if not flag:
                raise Exception('memcache client set failure, cache key: %s' % cache_key)
    
    
    def add(self, key, value, timeout=0, min_compress=50):
        """
        timeout:过期时间
        min_compress:压缩
        """
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        return self._current.set(force_str(key), value, timeout or self.default_timeout, min_compress)
    
    def get_data(self, model_cls, pkey):
        """
        model_cls:  model类对象
        pkey:       model对象主键
        """
        cache_key = model_cls.generate_cache_key(pkey)
        val = self._current.get(cache_key)
        if val is None:
            return None
        return pickle.loads(val)
    
    def get(self, key, default=None):
        """
        这里取2遍 如果实在去不到就return None
        """
        try:
            val = self._current.get(force_str(key))
        except:
            val = self._current.get(force_str(key))    
        if val is None:
            return default
        return val
    
    def set(self, key, value, timeout=0, min_compress=50):
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        try:
            return self._current.set(force_str(key), value, timeout or self.default_timeout, min_compress)
        except:
            return self._current.set(force_str(key), value, timeout or self.default_timeout, min_compress)
    
    def delete(self, key):
        try:
            try:
                val = self._current.delete(force_str(key))
            except:
                val = self._current.delete(force_str(key))
            if type(val)==bool:
                val = 1
        except:
            val = 0
        return val
    
    def get_multi(self, keys):
        """
        获取多个key 返回字典类型  {key:value,....}
        """
        return self._current.get_multi(map(force_str, keys))
    
    def incr(self, key, delta=1):
        return self._current.incr(key, delta)
    
    def decr(self, key, delta=1):
        """
        自增变量加上delta，默认加delta = 1
        """
        return self._current.decr(key, delta)
    
    def current(self):
        return self._current

