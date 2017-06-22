#coding=utf-8
from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User

import datetime
#from audit_log.models.managers import AuditLog

DEFAULT_EXPIRE = 7200     # 2 hour
DEFAULT_RETRY = 3600      # 1 hour
DEFAULT_REFRESH = 604800  # 1 week
DEFAULT_MINIMUM = 86400   # 1 day

# Create your models here.
class Region(models.Model):
    name = models.CharField(max_length=20,unique=True)
    memo = models.TextField(max_length=255,null=True)
    add_time = models.DateTimeField(auto_now_add=True)
    dnssec_keygen = models.CharField(max_length=256,null=True)

    def __str__(self):
        return self.name

    class Meta:
       db_table = 'region'

class Network(models.Model):
    ip_range = models.CharField(max_length=18, default='172.16.0.0/24')
    region = models.ForeignKey(Region,default=2)

    def __str__(self):
        return self.ip_range

    class Meta:
        db_table = 'network'

class Domain(models.Model):
    name = models.CharField(max_length=64,unique=True)
    memo = models.TextField(max_length=255,null=True,blank=True)
    add_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'domain'

class Record(models.Model):
    """record"""
    domain = models.ForeignKey('Domain')
    sub_domain = models.CharField(u'主机记录',max_length=80,default='@')
    record_type = models.ForeignKey('RecordType',verbose_name='记录类型')
    region = models.ForeignKey('Region',verbose_name=u'线路类型')
    value = models.CharField(u'记录值',max_length=64)
    weight = models.PositiveIntegerField(u'权重值',null=True,blank=True)
    mx_priority = models.PositiveIntegerField(u'mx优先级',null=True,blank=True)
    ttl = models.CharField(max_length=20, blank=True, default=600)
    update_time = models.DateTimeField(auto_now=True)
    add_time = models.DateTimeField(auto_now_add=True)
    operator = models.ForeignKey(User, related_name='records', null=True)

#    audit_log = AuditLog()

    def __str__(self):
        return "domain:" +self.domain.name + "||" +"region:" + self.region.name

    class Meta:
        db_table = 'record'
        unique_together = ('domain','sub_domain','region','value')

class RecordType(models.Model):
    """record type"""
    name = models.CharField(null=False,max_length=10,unique=True)
    memo = models.TextField(max_length=255,null=True,blank=True)
    add_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'record_type'

class SOA(models.Model):
    primary = models.CharField(u'主NS服务器',max_length=100)
    contact = models.CharField(u'管理员邮箱地址',max_length=100)
    serial = models.PositiveIntegerField(u'序列号',
        null=False, default=int(datetime.datetime.now().strftime('%Y%m%d01')))
    expire = models.PositiveIntegerField(u'过期时间',null=False, default=DEFAULT_EXPIRE)
    retry = models.PositiveIntegerField(u'重试时间',null=False, default=DEFAULT_RETRY)
    refresh = models.PositiveIntegerField(u'刷新时间',null=False, default=DEFAULT_REFRESH)
    minimum = models.PositiveIntegerField(u'否定答案有效时间',null=False, default=DEFAULT_MINIMUM)
    domain = models.ForeignKey(Domain, related_name='soa')

    class Meta:
        db_table = 'soa'

    @property
    def rdtype(self):
        return 'SOA'

    def render(self):
        return ("$TTL 86400\n"
                "@\t\tIN\t{0:5}\t{1:<20}\t{2:20} (\n"
                "\t\t\t\t{3:<20}\n"
                "\t\t\t\t{4:<20}\n"
                "\t\t\t\t{5:<20} \n"
                "\t\t\t\t{6})\n").format(
               self.rdtype, self.primary, self.contact, self.expire, self.retry, 
               self.refresh, self.minimum)

    def __str__(self):
        return self.domain.name

class JobStatus(models.Model):
    STATUS = (
        (0, u'等待执行'),
        (1, u'开始同步文件'),
        (2, u'同步文件失败'),
        (3, u'同步文件成功，正在重新加载配置'),
        (4, u'重新加载配置成功'),
        (5, u'重新加载配置失败'),
        (6, u'同步文件超时'),
        (7, u'重新加载配置超时'),
        (8, u'其他机器执行出错，停止操作'),
    )

    job_id = models.CharField(max_length=64)
    slave_ip = models.CharField(max_length=20)
    status = models.IntegerField(choices=STATUS, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'status'
