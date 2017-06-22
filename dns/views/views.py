#Author: Wang YiChen
#coding=utf-8

from django.http import HttpResponse,HttpResponseRedirect,Http404
from django.shortcuts import render
from dns.models import Region,Record,Domain,JobStatus
from dns.Validation import Valid
from nurse.settings import logger,BIND_DIR,slave_dir,slave_ip
from dns.utils import (make_view_dir,make_file,
                       write_to_file,generate_dnssec_key,
                       render_view_all_zone_data,
                       render_named_conf,backup_conf)
from django.core.exceptions import ObjectDoesNotExist
from dns.tasks import sync_named_conf
from dns.easyzone.tools import Named

import json
import os
import uuid
import subprocess
import traceback
import shutil

"""
view for views
"""

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

def index(request):
	return render('index.html')

def view_show(request):
    Region_obj = Region.objects.all()
    return render(request,'dns/view_show.html',locals())

def view_add(request):
    result = {'status':False,'error':''}
    if request.method == 'POST':
        view = request.POST.get('view','')
        memo = request.POST.get('memo','')
        if not view:
            result['error'] = u"view 不能为空"
            return HttpResponse(json.dumps(result))
        if view not in "default":
            try:
                default = Region.objects.get(name='default')
            except ObjectDoesNotExist:
                result['error'] = u"请先创建default线路"
                return HttpResponse(json.dumps(result))
        try:
            backup_conf(BIND_DIR)
            region_obj = Region(name=view,memo=memo)
            region_obj.dnssec_keygen = generate_dnssec_key() #generate the key
            region_obj.save()
            #创建master/slave view目录
            make_view_dir(view)
            make_view_dir(view,node='slave')

            #生成master/slave 的view.all.zone,并导入数据
            all_zone_master = render_view_all_zone_data(view=view)
            all_zone_slave = render_view_all_zone_data(view=view,node='slave')
            view_include_zone_file_master = os.path.join(BIND_DIR,
                                                         '%s.all.zone'%view)
            view_include_zone_file_slave = os.path.join(slave_dir,
                                                        '%s.all.zone'%view)
            if not write_to_file(view_include_zone_file_master,all_zone_master):
                result['error'] = u'master节点,%s.all.zone文件内容添加失败'%(view)
                return render(request,'dns/domain_add.html',locals())
            if not write_to_file(view_include_zone_file_slave,all_zone_slave):
                result['error'] = u'slave节点,%s.all.zone文件内容添加失败'%(view)
                return render(request,'dns/domain_add.html',locals())
            #创建zone 文件
            domains = Domain.objects.all()
            for domain in domains:
                view_dir = os.path.join(BIND_DIR,view)
                zone_filename = os.path.join(view_dir,domain.name +'.zone')
                make_file(zone_filename)
            #渲染named.conf
            named_conf_master = render_named_conf()
            named_conf_slave = render_named_conf(node='slave')
            namedconf_file_master = os.path.join(BIND_DIR,'named.conf')
            namedconf_file_slave = os.path.join(slave_dir,'named.conf')
            if not write_to_file(namedconf_file_master,named_conf_master):
                result['error'] = u'%s线路配置文件写入失败'%(namedconf_file_master)
                return render(request,'dns/domain_add.html',locals())
            if not write_to_file(namedconf_file_slave,named_conf_slave):
                result['error'] = u'%s线路配置文件写入失败'%(namedconf_file_slave)
                return render(request,'dns/domain_add.html',locals())
            #将所有已存在的default线路的record,复制到当前view
            default_region = Region.objects.filter(name='default')
            if view not in default_region:
                all_record = Record.objects.filter(region=default_region)
                for record in all_record:
                    record.pk = None
                    record.region = region_obj
                    record.save()

            #主节点推送配置文件并重启
            # named = Named()
            # is_restarted = named.restart()
            # if not is_restarted:
            #     result['error'] = u'主节点重启失败,请手动重启检查'
            #     return HttpResponse(json.dumps(result))
            #主节点重启
            named = Named()
            is_restarted = named.restart()
            if not is_restarted:
                result['error'] = u'主节点重启失败,请手动重启检查'
                return HttpResponse(json.dumps(result))
            #推送配置到从节点并重启
            for ip in slave_ip.split(','):
                jobstatus = JobStatus(job_id=str(uuid.uuid4()), slave_ip=ip)
                jobstatus.save()
                sync_named_conf.delay(job_id=jobstatus.job_id,src=slave_dir,
                                      dest=os.path.dirname(slave_dir),slave_ip=ip,
                                      ssh_port=21987)

            result['status'] = True
            return HttpResponse(json.dumps(result))
        except Exception as e:
            Region.objects.get(name=view).delete()
            logger.error(e)
            result['error'] = str(e)
            traceback.print_exc(e)
            return HttpResponse(json.dumps(result))

    return render(request,'dns/view_add.html')


def view_delete(request,view_id):

    result = {'status':False,'error':''}
    try:
        #删除此线路所有记录
        Record.objects.filter(region_id=int(view_id)).delete()
        #删除线路目录及其下面所有zone记录
        view_name = Region.objects.get(pk=int(view_id)).name
        dir_for_master = os.path.join(BIND_DIR,view_name)
        dir_for_slave = os.path.join(slave_dir,view_name)
        shutil.rmtree(dir_for_master)
        shutil.rmtree(dir_for_slave)
        #删除view.all.zone
        view_all_zone_file_from_master = os.path.join(BIND_DIR,
                                                     view_name + '.all.zone')
        view_all_zone_file_from_slave = os.path.join(slave_dir,
                                                    view_name + '.all.zone')
        os.remove(view_all_zone_file_from_master)
        os.remove(view_all_zone_file_from_slave)
        #删除数据库view
        Region.objects.filter(pk=int(view_id)).delete()
        #刷新named.conf配置
        named_conf_master = render_named_conf()
        named_conf_slave = render_named_conf(node='slave')
        namedconf_file_master = os.path.join(BIND_DIR,'named.conf')
        namedconf_file_slave = os.path.join(slave_dir,'named.conf')
        if not write_to_file(namedconf_file_master,named_conf_master):
            result['error'] = u'%s线路添加失败'%(namedconf_file_master)
            return HttpResponse(json.dumps(result))
        if not write_to_file(namedconf_file_slave,named_conf_slave):
            result['error'] = u'%s线路添加失败'%(namedconf_file_slave)
            return HttpResponse(json.dumps(result))
        #主节点重启
        named = Named()
        is_restarted = named.restart()
        if not is_restarted:
            result['error'] = u'主节点重启失败,请手动重启检查'
            return HttpResponse(json.dumps(result))
        #推送配置到从节点并重启
        for ip in slave_ip.split(','):
            jobstatus = JobStatus(job_id=str(uuid.uuid4()), slave_ip=ip)
            jobstatus.save()
            sync_named_conf.delay(job_id=jobstatus.job_id,src=slave_dir,
                                  dest=os.path.dirname(slave_dir),slave_ip=ip,ssh_port=21987)

        result['status'] = True
        print('重启成功了')
        return HttpResponse(json.dumps(result))

    except Exception as e:
        traceback.print_exc()
        result['error'] = u'删除失败'
        return HttpResponse(json.dump(result))
