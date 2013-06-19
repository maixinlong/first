#-*- coding: utf-8 -*-
"""
author:刘欣
redis封装 客户端
"""
import redis
import pickle
    

def force_str(text, encoding="utf-8", errors='strict'):
    t_type = type(text)
    if t_type == str:
        return text
    elif t_type == unicode:
        return text.encode(encoding, errors)
    return str(text)

class RedisClient(object):
    
    def __init__(self,config):
        '''
        servers is a string like "121.199.7.23:11211;42.121.145.76:11211"
        '''
        host = config['host']
        port = config['port']
        db = config['db']
        
        self._current = redis.Redis(host=host, port=port, db=db)
    
    def put_data(self, model_cls, pkey, data, create_new):
        #获取保存的key   类似 key|app.modles.friend|用户id
        cache_key = model_cls.generate_cache_key(pkey)
        #先dumps 转成二进制 序列化 1和2是二进制  HIGHEST_PROTOCOL:是2  快而剩空间
        val = pickle.dumps(data, pickle.HIGHEST_PROTOCOL)
        if create_new:
            flag = self._current.add(cache_key, val)
            if not flag:
                raise Exception('redis client add failure, cache key: %s' % cache_key)
        else:
            flag = self._current.set(cache_key, val)
            if not flag:
                raise Exception('redis client set failure, cache key: %s' % cache_key)
    
    def add(self, key, value, timeout=0, min_compress=50):
        """
        timeout:过期时间
        min_compress:压缩
        """
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        return self._current.set(force_str(key), value)
    
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
            return self._current.set(force_str(key), value)
        except:
            return self._current.set(force_str(key), value)
    
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
    
    def current(self):
        return self._current

