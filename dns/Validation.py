#Author: Wang YiChen
#coding=utf-8

import re



class Valid(object):
    def __init__(self,type):
        self.type = type

    def __call__(self,data):
        if self.type == 'NS':
            return self.is_valid_domain(data)
        elif self.type == 'A':
            return self.is_valid_ip(data)
        elif self.type == 'CNAME':
            return self.is_valid_domain(data)
        elif self.type == 'MX':
            return self.is_valid_domain(data)
        else:
            raise KeyError('no match for this type name!')

    @staticmethod
    def is_valid_domain(domain):
        filter = re.compile(r'^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}'
                            '[a-zA-Z0-9])?\.)+[a-zA-Z]{2,6}\.?$')
        result = filter.match(domain)
        return True if result else False

    @staticmethod
    def is_valid_ip(ip):
        ip_filter = re.compile(r'^((([1-9]?|1\d)\d|2([0-4]\d|5[0-5]))\.)'
                                '{3}(([1-9]?|1\d)\d|2([0-4]\d|5[0-5]))$')
        result = ip_filter.match(ip)
        return True if result else False

    @staticmethod
    def record_value(value):
        pass

