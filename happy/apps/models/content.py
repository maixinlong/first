#coding=utf-8

from datetime import date
from models.engine import Engine
import datetime

class Content(Engine):
    
    def __init__(self,uid):
        Engine.__init__(self)
        
        self.uid = uid              #时间
        self.weibo = {}             #微博内容 {'段子':{'用户':[]}}
        self.other_info = {}        #扩展信息
        
    @classmethod
    def _install(cls, uid):
        """为新用户初始安装好友信息
        Args:
            uid: 用户ID
        Returns:
            weibo: 用户好友信息对象实例
        """
        content = cls(uid)
        content.put()
        return content
    
    @classmethod
    def get(cls, uid):
        obj = super(Content, cls).get(uid)
        return obj
    
        


