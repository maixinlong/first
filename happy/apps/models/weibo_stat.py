#coding=utf-8

"""
微博的统计信息
"""

from datetime import date
from models.engine import Engine
import datetime

class WeiboStat(Engine):
    
    def __init__(self,time_s):
        Engine.__init__(self)
        
        self.uid = time_s              # 用户ID
        
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
    
        


