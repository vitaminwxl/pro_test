#coding=utf-8
from __future__ import unicode_literals
from django.contrib.auth.models import AbstractBaseUser,UserManager
from django.db import models

import time
# Create your models here.

class User(AbstractBaseUser):
    USER_ROLE_CHOICES = (
        ('SU','SuperUser'),
        ('CU','CommonUser'),
    )
    name = models.CharField(u'姓名',max_length=100,unique=True)
    email = models.EmailField(u'邮件',max_length=100,unique=True)
    date_joined = models.DateTimeField(u'创建时间',blank=True,auto_now_add=True)
    memo = models.CharField(u'备注',blank=True,null=True,default=None,max_length=200)
    tel = models.CharField(u'手机',max_length=32,default=None,blank=True,null=True)
    role_type = models.CharField(u'角色',choices=USER_ROLE_CHOICES,max_length=16,unique=True)

    objects = UserManager()

    USERNAME_FIELD = 'name'
    REQUIRED_FIELDS = ('email',)

    class Meta:
        db_table = 'User'
        verbose_name = u'用户管理'
        verbose_name_plural = u'用户管理'

    def get_full_name(self):
        return self.email

    def get_short_name(self):
        return self.name

    def __unicode__(self):
        return self.name


