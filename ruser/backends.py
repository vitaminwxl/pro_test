#coding=utf-8
__author__ = 'WangYiChen'
from django.contrib.auth import authenticate
from nurse.auth.LDAPLogin import LdapAuth
import ldap
from django.contrib.auth.models import User

ad_addr = 'ldap://ds.gome.com.cn'


def ad_check(username, password):
    domain_user = 'DS\\' + username
    print domain_user
    try:
        l = ldap.initialize(ad_addr)
        l.simple_bind_s(domain_user, password)
        print "111111"
        return True
    except:
        print "222222"
        return False


class LdapBackend(object):
    def authenticate(self,username=None,password=None):
        is_login = ad_check(username, password)
        if is_login:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                #Create a new user. Note that we can set password
                #to anything,because it won't be checked;the password
                #from ldap will
                user = User(username=username)
                user.set_password(password)
                user.is_staff = True
                #user.is_superuser = True
                user.save()
            return user
            print user.username
        return None

    def get_user(self,user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


