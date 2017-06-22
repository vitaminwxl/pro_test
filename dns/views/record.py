#coding=utf-8
from django.shortcuts import render,get_object_or_404
from django.http import HttpResponse,HttpResponseRedirect,Http404
from django.core.urlresolvers import reverse,resolve
from dns.models import Record,RecordType,Domain,Region,SOA,JobStatus
from nurse.settings import BIND_DIR,slave_dir,slave_ip
from dns import models
from dns.utils import make_file,write_to_file
from dns.Validation import Valid
from nurse.settings import logger
from jinja2 import Environment,FileSystemLoader
from dns.easyzone.tools import NamedCheck,Named
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from dns.tasks import sync_named_conf

import json
import datetime
import uuid
import os
import sys
import traceback

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

def index(request):
    return render('index.html')

@login_required
def domain_show(request):
    url_resovle_obj = resolve(request.path_info)
    domain_obj = Domain.objects.all()
    return render(request,'dns/domain_show.html',locals())

@login_required
def domain_add(request):
    """
    :param request:
    :return: {status:True,error:''}
    """
    result = {'status':False,'error':u'Server Error!'}
    error=''
    if request.method == 'POST':
        domain = request.POST.get('domain_name','')
        memo = request.POST.get('memo','')
        hostname = request.POST.get('hostname','')
        email = request.POST.get('M_email','')
        serial = request.POST.get('serial','')
        refresh = request.POST.get('refresh','')
        retry = request.POST.get('retry','')
        expire = request.POST.get('expire','')
        ttl = request.POST.get('ttl')
        if Valid.is_valid_domain(domain):
            try:
                #在每个view目录下批量创建zone数据库文件,同时向view_all.zone 文件新增zone数据库文件
                views = Region.objects.all()
                domains = [zone.name for zone in Domain.objects.all()]
                if domain not in domains:
                    domains.append(domain)
                env = Environment(loader=FileSystemLoader(
                                    os.path.join(BASE_DIR,'template/default')),
                                    trim_blocks=True, lstrip_blocks=True)
                template = env.get_template('view.all.zone')
                for view in views:
                    view_dir = os.path.join(BIND_DIR,view.name)
                    zone_filename = os.path.join(view_dir,domain+'.zone')
                    make_file(zone_filename)
                    render_data = {
                        'domains': domains,
                        'view_dir': view_dir
                    }
                    render_data = template.render(render_data)
                    view_include_zone_file = os.path.join(BIND_DIR,'%s.all.zone'%view.name)
                    if not write_to_file(view_include_zone_file,render_data):
                        result['error'] = u'master节点,%s.all.zone文件内容添加失败'%(view.name)
                        return render(request,'dns/domain_add.html',locals())
                #生成slave节点的view.all.zone
                env = Environment(loader=FileSystemLoader(
                                os.path.join(BASE_DIR,'template/slave')),
                                trim_blocks=True, lstrip_blocks=True)
                template = env.get_template('view.all.zone')
                for view in views:
                    view_dir = os.path.join(slave_dir,view.name)
                    render_data = {
                        'domains': domains,
                        'view_dir': view_dir
                    }
                    render_data = template.render(render_data)
                    view_include_zone_file = os.path.join(slave_dir,'%s.all.zone'%view.name)
                    if not write_to_file(view_include_zone_file,render_data):
                        result['error'] = u'slave节点,%s.all.zone文件内容添加失败'%(view.name)
                        return render(request,'dns/domain_add.html',locals())
                ##restart the new zone
                reload = Named()
                if not reload.reload_conf():
                    result['error'] = reload.error
                    return HttpResponse(json.dumps(result))
                #推送从节点配置文件及重启
                for ip in slave_ip.split(','):
                    print(ip)
                    jobstatus = JobStatus(job_id=str(uuid.uuid4()), slave_ip=ip)
                    jobstatus.save()
                    sync_named_conf.delay(job_id=jobstatus.job_id,src=slave_dir,
                                          dest=os.path.dirname(slave_dir),slave_ip=ip,ssh_port=21987)
                ##添加数据到数据库
                domain_obj = Domain(name=domain,memo=memo)
                domain_obj.save()
                soa_obj = SOA(
                    primary=hostname,
                    contact=email,
                    serial=int(serial) if serial else int(
                            datetime.datetime.now().strftime('%Y%m%d01')),
                    expire=int(expire) if expire else models.DEFAULT_EXPIRE,
                    retry=int(retry) if retry else models.DEFAULT_RETRY,
                    refresh=int(refresh) if refresh else models.DEFAULT_REFRESH,
                    minimum=int(ttl) if ttl else models.DEFAULT_MINIMUM,
                    domain=domain_obj,
                )
                soa_obj.save()
                error = u'添加成功'
                return render(request,'dns/domain_add.html',locals())
            except Exception as e:
                logger.error(e)
                error = str(e)
                traceback.print_exc(e)
                return render(request,'dns/domain_add.html',locals())
        else:
            error = 'Wrong doamin!'
            render(request,'dns/domain_add.html',locals())
    return render(request,'dns/domain_add.html',locals())

@login_required
def domain_delete(request,domain_id):
    result = {'status':False,'error':''}
    try:
        #删除master节点文件数据(view.all.zone,domain.com.zone)
        domain = Domain.objects.get(id=int(domain_id)).name
        views = Region.objects.all()
        views = Region.objects.all()
        domains = [zone.name for zone in Domain.objects.all()]
        if domain in domains:
            domains.remove(domain)
        env = Environment(loader=FileSystemLoader(
                            os.path.join(BASE_DIR,'template/default')),
                            trim_blocks=True, lstrip_blocks=True)
        template = env.get_template('view.all.zone')
        for view in views:
            view_dir = os.path.join(BIND_DIR,view.name)
            zone_filename = os.path.join(view_dir,domain+'.zone')
            os.remove(zone_filename)
            render_data = {
                'domains': domains,
                'view_dir': view_dir
            }
            render_data = template.render(render_data)
            view_include_zone_file = os.path.join(BIND_DIR,'%s.all.zone'%view.name)
            if not write_to_file(view_include_zone_file,render_data):
                result['error'] = u'master节点,%s.all.zone文件内容修改失败'
                return HttpResponse(json.dumps(result))
        #删除slave节点文件数据(view.all.zone)
        env = Environment(loader=FileSystemLoader(
                            os.path.join(BASE_DIR,'template/slave')),
                            trim_blocks=True, lstrip_blocks=True)
        template = env.get_template('view.all.zone')
        for view in views:
            view_dir = os.path.join(slave_dir,view.name)
            render_data = {
                'domains': domains,
                'view_dir': view_dir
            }
            render_data = template.render(render_data)
            view_include_zone_file = os.path.join(slave_dir,'%s.all.zone'%view.name)
            if not write_to_file(view_include_zone_file,render_data):
                result['error'] = u'slave节点,%s.all.zone文件内容修改失败'%(view.name)
                return HttpResponse(json.dumps(result))
        ##restart the new zone
        reload = Named()
        if not reload.reload_conf():
            result['error'] = reload.error
            return HttpResponse(json.dumps(result))
        #推送从节点配置文件及重启
        for ip in slave_ip.split(','):
            jobstatus = JobStatus(job_id=str(uuid.uuid4()), slave_ip=ip)
            jobstatus.save()
            sync_named_conf.delay(job_id=jobstatus.job_id,src=slave_dir,
                                  dest=os.path.dirname(slave_dir),slave_ip=ip,ssh_port=21987)
        #删除数据库数据
        Record.objects.filter(domain_id=int(domain_id)).delete()
        Domain.objects.filter(pk=int(domain_id)).delete()
        SOA.objects.filter(domain_id=int(domain_id)).delete()
        result['status'] = True
        response = HttpResponse(json.dumps(result))
    except Exception as e:
        logger.error(e)
        traceback.print_exc(e)
        result['error'] = str(e)
        response = HttpResponse(json.dumps(result))
    return response

@login_required
def record_show(request,domain_id):
    result = {'status':False,'error':''}
    domain = get_object_or_404(Domain, pk=domain_id)
#    domain = Domain.objects.filter(pk=domain_id).exists()
    if domain:
        domain_obj = Domain.objects.get(pk=domain_id)
        records = Record.objects.filter(domain=int(domain_id))
        types = RecordType.objects.all()
        lines = Region.objects.all()
        return render(request,'dns/record_show.html',locals())
    else:
        return Http404("Domain does not exist")

@login_required
def record_add(request):
    if request.method == 'POST':
        result = {'status':False,'error':''}
        require_key = ['entry_name','entry_type','entry_value',
                       'entry_line','entry_mx','entry_weight','entry_ttl']
        domain_id = request.POST.get('domain_id')
        entry_name = request.POST.get('entry_name','@')
        entry_type = request.POST.get('entry_type','')
        entry_value = request.POST.get('entry_value','')
        entry_line  = request.POST.get('entry_line')
        entry_mx = request.POST.get('entry_mx',None)
        entry_weight = request.POST.get('entry_weight')
        entry_ttl = request.POST.get('entry_ttl','600')

        entry_mx = entry_mx if entry_mx else None
        entry_weight = entry_weight if entry_weight else None
        #验证数据
        types = {type.id:type.name  for type in RecordType.objects.all()}
        try:
            ##判断是否有default线路记录
            if Region.objects.get(pk=int(entry_line)).name != 'default':
                default_obj = Record.objects.filter(region__name='default',
                                                    sub_domain=entry_name,
                                                    record_type_id=int(entry_type),
                                                    domain_id=int(domain_id),
                                                    value = entry_value
                                                    )
                if not default_obj:
                    result['error'] = u'还没有添加默认线路的解析，请先添加为默认记录'
                    return HttpResponse(json.dumps(result))
            if int(entry_type) in types:
                if not Valid(types[int(entry_type)])(entry_value):
                    result['error'] = u'记录值不正确'
                    return HttpResponse(json.dumps(result))
        except Exception as e:
            logger.error(e)
            traceback.print_exc(e)
            result['error'] = 'Server Error!'
            return HttpResponse(json.dumps(result))
        try:
            #插入数据
            obj = Record(domain_id=int(domain_id),sub_domain=entry_name,
                         value=entry_value,weight=entry_weight,
                         mx_priority=entry_mx,ttl=int(entry_ttl),
                         record_type_id=int(entry_type),region_id=int(entry_line),operator=request.user)
            obj.save()
            current_view = Region.objects.get(pk=int(entry_line)).name
            #如果是添加默认线路记录,遍历每个线路,是否存在这个记录,不存在就设置成默认线路记录
            if current_view == 'default':
                Regions = Region.objects.all()
                for region in Region.objects.all():
                    try:
                        Record.objects.get(domain_id=int(domain_id),
                                                 sub_domain=entry_name,
                                                 value=entry_value,
                                                 region=region)
                    except ObjectDoesNotExist:
                        obj = Record(domain_id=int(domain_id),
                                     sub_domain=entry_name,
                                     value=entry_value,
                                     weight=entry_weight,
                                     mx_priority=entry_mx,
                                     ttl=int(entry_ttl),
                                     record_type_id=int(entry_type),
                                     region=region,operator=request.user)
                        obj.save()
            result['status'] = True
            return HttpResponse(json.dumps(result))
        except Exception as e:
            logger.error(e)
            traceback.print_exc(e)
            result['error'] = u'Server Error.'
            return HttpResponse(json.dumps(result))

def record_del(request):
    result = {'status':False,'error':''}
    if request.method == 'POST':
        try:
            record_id = request.POST.get('record_id')
            if record_id:
                deleted,del_info = Record.objects.filter(id=int(record_id)).delete()
                if deleted:
                    result['status'] = True
                    return HttpResponse(json.dumps(result))
                else:
                    result['error']=u'记录不存在'
                    return HttpResponse(json.dumps(result))
        except Exception as e:
            traceback.print_exc(e)
    return HttpResponse('401')

@login_required
def record_edit(request):
        if request.method == 'POST':
            result = {'status':False,'error':''}
            require_key = ['entry_name','entry_type','entry_value',
                           'entry_line','entry_mx','entry_weight','entry_ttl']

            entry_id = request.POST.get('entry_id')
            entry_name = request.POST.get('entry_name')
            entry_type = request.POST.get('entry_type')
            entry_value = request.POST.get('entry_value')
            entry_line  = request.POST.get('entry_line')
            entry_mx = request.POST.get('entry_mx')
            entry_weight = request.POST.get('entry_weight')
            entry_ttl = request.POST.get('entry_ttl')
            try:
                #插入数据
                entry_mx = int(entry_mx) if entry_mx else None
                entry_weight = int(entry_weight) if entry_weight else None
                obj = Record.objects.get(id=int(entry_id))
                obj.sub_domain = entry_name
                obj.record_type_id = int(entry_type)
                obj.value = entry_value
                obj.region_id = int(entry_line)
                obj.mx_priority = entry_mx
                obj.weight = entry_weight
                obj.ttl = int(entry_ttl)
		obj.operator = request.user
                obj.save()
                result['status'] = True
                return HttpResponse(json.dumps(result))
            except Exception as e:
                logger.error(e)
                traceback.print_exc(e)
                result['error'] = u'Server Error.'
                return HttpResponse(json.dumps(result))
        return HttpResponse('401')


@login_required
def soa_settings(request,domain_id):
    pass

@login_required
def acl_list(request):
    #view_dict = {obj.view_name:int(obj.id) for obj in View.objects.all()}
    # view_objs= View.objects.all()
    # acl_objs = ACL.objects.all()
    return render(request,'dns/acl_list.html',locals())

@login_required
def acl_add(request):
    if request.method == 'POST':
        return HttpResponse(json.dumps({'status':True,'error':''}))

    return render(request,'dns/acl_add.html')



