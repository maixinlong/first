#coding=utf-8

from datetime import date
from models.engine import Engine
import datetime

class Weibo(Engine):
    
    def __init__(self,uid):
        Engine.__init__(self)
        
        self.uid = uid              # 用户ID
        self.statuses_count = 0     #微博数
        self.followers_count = 0    #粉丝数
        self.profile_image_url = "" #用户小头像地址
        self.avatar_large = ""      #用户大头像地址
        self.stat_info = {}          #当前微博用户的统计信息
        self.other_info = {}        # 扩展信息
        
    @classmethod
    def _install(cls, uid):
        """为新用户初始安装好友信息
        Args:
            uid: 用户ID
        Returns:
            weibo: 用户好友信息对象实例
        """
        weibo = cls(uid)
        weibo.put()
        return weibo
    
    @classmethod
    def get(cls, uid):
        obj = super(Weibo, cls).get(uid)
        return obj
    
        


