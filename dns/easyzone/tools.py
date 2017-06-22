#coding=utf-8
from __future__ import unicode_literals
__author__ = 'WangYiChen'

import subprocess
from nurse import settings

class ZoneReloadError(Exception):
    "自定义错误"
    pass


class Named(object):

    def __init__(self,rndc=settings.rndc,view='default'):
        self.rndc = rndc
        self.view = view
        self.error = None

    def reload_zone(self,zone):
        cmd = [
            self.rndc,
            'reload',
            zone,
            'IN',
            self.view
        ]
        r = subprocess.call(cmd)
        if r != 0:
            self.error='[{0}]rndc failed with return code {1}'.format(zone,r)
            return False
        else:
            return True

    def reload_conf(self):
        cmd = [
            self.rndc,
            'reload'
        ]
        r = subprocess.call(cmd)
        if r != 0:
            self.error='rndc failed with return code {0}'.format(r)
            return False
        else:
            return True

    def restart(self,named=settings.named):
        cmd = [
            named,
            'restart'
        ]
        r = subprocess.call(cmd)
        if r != 0:
            self.error='named restart failed with return code {0}'.format(r)
        else:
            return True



class NamedCheck(object):

    def __init__(self,checkzone=settings.named_checkzone,
                 checkconf=settings.named_checkconf):
        self.checkzone = checkzone
        self.checkconf = checkconf
        self.error = None

    def check_zone(self,zonename,filename):
        cmd = [
            self.checkzone,
            '-q',
            zonename,
            filename
        ]
        print(cmd)
        r = subprocess.call(cmd)
        print(r)
        if r != 0:
            self.error = u'配置文件检查语法错误:路径地址[%s]'%(filename)
            return False
        else:
            self.error = None
            return True

    def check_conf(self,filename):
        cmd = [
            self.checkconf,
            filename
        ]
        r = subprocess.call(cmd)
        if r != 0:
            self.error = 'Bad syntax in [%s],please check.'%(filename)
            return False
        else:
            return True

    @staticmethod
    def bash(cmd,filename):
        r = subprocess.call(cmd)
        if r != 0:
            self.error = 'Bad syntax in [%s],please check.'%(filename)
            return False
        else:
            return True

if __name__ == "__main__":
    try:
        is_valid = NamedCheck()
        if not is_valid.check_conf('/etc/named.conf'):
            print(is_valid.error)
        if not is_valid.check_zone('wangyichen.com','/var/named/wangyichen.com.zone.int'):
            print(is_valid.error)
        rndc = ZoneReload(view='INT')
        rndc.reload('wangyichen.com')
    except Exception as e:
        print(str(e))



