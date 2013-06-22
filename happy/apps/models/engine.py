#coding=utf-8

"""
数据存储封装 可以添加多个缓存来写入
当前版本还未添加 mysql层的写入 先只针对缓存层 + 定时写入mysql  后期有时间再加上
author:刘欣
"""
from django.conf import settings
import pickle
import copy

#engins = settings.ENGINS
engins = {"redis" : {
        "class" : "cache.redis_client.RedisClient",
        "config" : {
            "host" : "localhost",
            "port" : 6379,
            "db":1,
             }
        },
      }

def import_by_name(name):
    """
    动态导入
    """
    tmp = name.split(".")
    module_name = ".".join(tmp[0:-1])
    obj_name = tmp[-1]
    module = __import__(module_name, globals(), locals(), [obj_name]) 
    
    return getattr(module, obj_name)

#获取存储实例
app = {}
for engine_name,engine in engins.iteritems():
    engine_class = engine['class']
    engine_conf = engine['config']
    obj = import_by_name(engine_class)
    app[engine_name] = obj(engine_conf)
    
class Engine(object):

    def __init__(self):
        
        super(Engine, self).__init__()
    

    @classmethod
    def generate_cache_key(cls, pkey):
        """
        生成key
        """
        return 'FIRST|MEMCACHE' + "|" + cls.__module__ + "." + cls.__name__ + '|' + str(pkey)    
    
    def get_pkey(self):
        """
        根据子类对象获取key
        """
        return self.__class__.generate_cache_key(str(self.uid))
        
    @classmethod
    def get(cls, pkey):
        """
        cache_key:cache key
        pkey:uid 唯一标示
        """
        data = None
        level = 0
        cache_key = cls.generate_cache_key(pkey)
        # 从存储层获取dumps后的对象数据  对应这配置文件的 现在就配置了 memcached  还可以有其他的 mysql redis等等
        for engine_name in engins:
            #根据配置的引擎 获取一个对象 比如memcache的实例
            engine_obj = app[engine_name]
            level += 1
            data = engine_obj.get_data(cls, cache_key)
            #如果取到了 就不再 遍历
            if data is not None:
                break
        #如果实在取不到就是没有数据
        if data is None:
            return None
        
        # 获取到dumps数据，转换成为对象实例  这时候对象是 字典类型的 
        #如果从底层数据库中读取出来的  再缓存到更上层cache中
        obj = pickle.loads(data)
        if level > 1:
            top_engine_obj = app[engins.keys()[0]]
            top_engine_obj.put_data(cls, cache_key, data, False)
            
        return obj
            
    def put(self):
        cls = self.__class__
        data = pickle.dumps(self)
        pkey = self.get_pkey()
        print pkey
        for engine_name in engins:
            engine_obj = app[engine_name]
            engine_obj.put_data(cls, pkey, data, False)
    
    def put_only_bottom(self):
        """直接写到存储的最底一层
        """
        cls = self.__class__
        data = self.dumps()
        pkey = self.get_pkey()
        engine_obj = app[engins.keys()[-1]]
        engine_obj.put_data(cls, pkey, data, self.need_insert)

    def do_delete(self):
        cls = self.__class__
        pkey = self.get_pkey()
        for engine_name in engins:
            engine_obj = app[engine_name]
            engine_obj.delete_data(cls, pkey)
