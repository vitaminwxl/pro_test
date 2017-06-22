#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-
 
import  ldap
import ConfigParser
import os
import traceback

__all__ = ['GetDn','LDAPLogin']
'''
    实现LDAP用户登陆验证,首先获取用户的DN条目,然后再验证用户名和密码
'''

# config = ConfigParser.ConfigParser()
# BASE_DIR = os.path.dirname(os.path.dirname(
#                            os.path.dirname(os.path.abspath(__file__))))
# config.read(os.path.join(BASE_DIR, 'nurse.conf'))
# print(os.path.join(BASE_DIR, 'nurse.conf'))
# ldappath = config.get('ldap', 'ldappath')
# ldapuser = config.get('ldap', 'ldapuser')
# ldappass = config.get('ldap', 'ldappass')
# baseDN = config.get('ldap', 'baseDN')

ldappath = "ldap://ldap.gomeo2o.cn:389/"
ldappath = "ldap://10.69.213.21:389/"
baseDN = "ou=People,dc=ldap,dc=gomeo2o,dc=cn"
ldapuser = "cn=Manager,dc=ldap,dc=gomeo2o,dc=cn";
ldappass = "xrwfvyBBBT!DkK05"
# baseDN = "dc=ldap,dc=gomeo2o,dc=cn"

LdapConf = {
    'ldappath': "ldap://ldap.gomeo2o.cn:389/",
    'baseDN'  : "ou=People,dc=ldap,dc=gomeo2o,dc=cn",
    "ldapuser": "cn=Manager,dc=ldap,dc=gomeo2o,dc=cn",
    'ldappass': "xrwfvyBBBT!DkK05"
}

class LdapAuth(object):
    def __init__(self,username=None,password=None):
        self._username = username
        self._password = password
        self.error = None
        self._ldappath = "ldap://10.69.213.21:389/"
        self._baseDN  = "ou=People,dc=ldap,dc=gomeo2o,dc=cn"
        self._ldapuser = "cn=Manager,dc=ldap,dc=gomeo2o,dc=cn"
        self._ldappass = "xrwfvyBBBT!DkK05"

    def _validateLDAPUser(self):
        try:
            l = ldap.initialize(self._ldappath)
            l.protocol_version = ldap.VERSION3
            l.simple_bind(self._ldapuser, self._ldappass)
            searchScope  = ldap.SCOPE_SUBTREE
            searchFiltername = "cn"
            retrieveAttributes = None
            searchFilter = '(' + searchFiltername + "=" + self._username +')'

            ldap_result_id = l.search(self._baseDN,
                                      searchScope,
                                      searchFilter,
                                      retrieveAttributes)
            result_type, result_data = l.result(ldap_result_id,1)
            if(not len(result_data) == 0):
              return 1, result_data[0][0]
            else:
              return 0, ''
        except ldap.LDAPError, e:
            print e
            return 0, ''
        finally:
            l.unbind()
            del l

    def GetDn(self,trynum = 30):
        """
        :param user: LDAP User
        :param trynum:  Retry count
        :return: 'cn=wangyichen,ou=People,dc=ldap,dc=gomeo2o,dc=cn' or ""
        """
        i = 0
        isfound = 0
        foundResult = ""
        while(i < trynum):
            isfound, foundResult = self._validateLDAPUser()
            if(isfound):
              break
            i+=1
        return foundResult

    def LDAPLogin(self):
        try:
            if(self._password == ""):
                self.error = "Password cannot be empty"
                return False
            dn = self.GetDn(10)
            if(dn==''):
                self.error = "The user does not exist,please apply for LDAP permissions"
                return False
            my_ldap = ldap.initialize(self._ldappath)
            my_ldap.simple_bind_s(dn,self._password)
            return True
        except Exception,e:
            traceback.print_exc(e)
            self.error = "用户名或者密码错误, 请重新输入正确的用户名或密码"
            return False
