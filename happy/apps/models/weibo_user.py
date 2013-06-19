#coding=utf-8

from datetime import date
from models.engine import Engine
import datetime

uid = "user_weibo"
class WeiboUser(Engine):
    
    def __init__(self):
        """
        存放不同类别的 微博用户
        """
        Engine.__init__(self)
        
        self.uid = uid              #用户ID
        self.users = {}     #{'旅游':[]}
        self.userids = {}      
        self.other_info = {}
        
    @classmethod
    def _install(cls):
        """为新用户初始安装好友信息
        """
        weibo = cls('user_weibo')
        weibo.put()
        return weibo
    
    @classmethod
    def get(cls):
        obj = super(WeiboUser, cls).get(uid)
        return obj
    
        


