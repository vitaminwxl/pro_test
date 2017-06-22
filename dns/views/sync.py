#coding=utf-8
__author__ = 'WangYiChen'

from django.http import HttpResponse
from dns.models import Domain,Record,Region,SOA
from nurse.settings import BIND_DIR,BASE_DIR
from jinja2 import Environment,FileSystemLoader
from time import localtime,strftime,time
from dns.utils import backup_conf,write_to_file
from nurse.settings import logger
from dns.easyzone.tools import Named,NamedCheck
from jinja2 import FileSystemLoader,Environment
from django.contrib.auth.decorators import login_required

import os
import json
import traceback
from time import localtime,strftime,time
BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


@login_required
def sync_record(request):
    try:
        result = {'status':False,'error':''}
        domain_id = request.POST.get('domain_id')
        domain_obj = Domain.objects.get(pk=int(domain_id))
        domain_name = domain_obj.name
        Region_all = Region.objects.all()

        #soa serial 自增
        soa = SOA.objects.get(domain=domain_obj)
        new_serial = int(strftime('%Y%m%d00', localtime(time())))
        if new_serial <= soa.serial:
            soa.serial = soa.serial + 1
            soa.save()
        else:
            soa.serial = new_serial
            soa.save()
        soa_data = {
            'primary': soa.primary,
            'contact': soa.contact,
            'serial' : soa.serial,
            'expire' : soa.expire,
            'retry'  : soa.retry,
            'refresh': soa.refresh,
            'minimum': soa.minimum
        }

        env = Environment(loader=FileSystemLoader(
                os.path.join(BASE_DIR,'template/default')),trim_blocks=True, lstrip_blocks=True)
        is_success = backup_conf(BIND_DIR) #备份文件
        if not is_success:
            result['error'] = '同步文件不成功,备份文件失败'
            return HttpResponse(json.dumps(result))
    except Exception as e:
        traceback.print_exc(e)
        logger.error(str(e))
        result['error'] = '同步文件失败'
        return HttpResponse(json.dumps(result))

    try:
        #同步数据库数据到配置文件
        for region in Region_all:
            records = Record.objects.filter(domain=domain_obj,region=region)
            zone_file = os.path.join(os.path.join(BIND_DIR,region.name),domain_name + '.zone')
            template = env.get_template('defaultzone.j2')
            """
            预留//第一次添加域名时候,输入完default线路记录之后,
            同步的时候,判断当前view是否有记录,没有记录的话,同步default的记录到此view下面
            """
            ns_list = [ {"sub_domain": record.sub_domain,
                         "value": record.value, "ttl": record.ttl}
                        for record in records if record.record_type.name == "NS"]
            mx_list = [ {"sub_domain": record.sub_domain,
                         "value": record.value, "ttl": record.ttl,
                         "mx_priority": record.mx_priority}
                        for record in records if record.record_type.name == "MX"]
            a_list = [ {"sub_domain": record.sub_domain, "value": record.value,
                        "ttl": record.ttl}
                        for record in records if record.record_type.name == "A"]
            cname_list = [ {"sub_domain": record.sub_domain, "value": record.value,
                            "ttl": record.ttl} for record in records
                           if record.record_type.name == "CNAME"]
            if not ns_list:  #当其他线路没有配置NS的时候,同步default线路数据到其他线路
                default_region = Region.objects.get(name='default')
                records = Record.objects.filter(domain=domain_obj,region=default_region)

                ns_list = [ {"sub_domain": record.sub_domain,
                         "value": record.value, "ttl": record.ttl}
                        for record in records if record.record_type.name == "NS"]
                mx_list = [ {"sub_domain": record.sub_domain,
                         "value": record.value, "ttl": record.ttl,
                         "mx_priority": record.mx_priority}
                        for record in records if record.record_type.name == "MX"]
                a_list = [ {"sub_domain": record.sub_domain, "value": record.value,
                        "ttl": record.ttl}
                        for record in records if record.record_type.name == "A"]
                cname_list = [ {"sub_domain": record.sub_domain, "value": record.value,
                            "ttl": record.ttl} for record in records
                           if record.record_type.name == "CNAME"]

            data = {
                'soa_dict'  : soa_data,
                'ns_list'   : ns_list,
                'mx_list'   : mx_list,
                'cname_list': cname_list,
                'a_list'    : a_list
            }
            render = template.render(**data)
            #written to the file
            if not write_to_file(zone_file,render):
                result['error'] = '同步文件失败'
                return HttpResponse(json.dumps(result))
            #Check the configuration file syntax
            is_valid = NamedCheck()
            if not is_valid.check_zone(domain_name,zone_file):
                result['error'] = is_valid.error
                return HttpResponse(json.dumps(result))
        #mult to reload
        for region in Region_all:
            rndc = Named(view=region.name)
            if domain_name == 'idc.pub' or domain_name == 'ds.gome.com.cn':
		continue
            if not rndc.reload_zone(domain_name):
                result['error'] = "reload failed view[{view}] domain[{domain}]".format(region.name,domain_name)
                return HttpResponse(json.dumps(result))
        result['status'] = True
        return HttpResponse(json.dumps(result))
    except Exception as e:
        traceback.print_exc(e)
        logger.error(e)
        result['error'] = '同步文件失败'
        return HttpResponse(json.dumps(result))

def sync_view(request,view_id):
    result = {'status':False,'error':''}
    is_success = backup_conf(BIND_DIR) #备份文件
    if not is_success:
        result['error'] = u'同步文件不成功,备份文件失败'
        return HttpResponse(json.dumps(result))
    try:
        region_obj = Region.objects.get(pk=int(view_id))
        region_name = region_obj.name
        all_domain = Domain.objects.all()
        for domain in all_domain:
            #get SOA
            soa = SOA.objects.get(domain=domain)
            soa_data = {
                'primary': soa.primary,
                'contact': soa.contact,
                'serial' : soa.serial,
                'expire' : soa.expire,
                'retry'  : soa.retry,
                'refresh': soa.refresh,
                'minimum': soa.minimum
            }
            #get record
            records = Record.objects.filter(region_id=int(view_id),domain=domain)
            ns_list = [ {"sub_domain": record.sub_domain,
                         "value": record.value, "ttl": record.ttl}
                        for record in records if record.record_type.name == "NS"]
            mx_list = [ {"sub_domain": record.sub_domain,
                         "value": record.value, "ttl": record.ttl,
                         "mx_priority": record.mx_priority}
                        for record in records if record.record_type.name == "MX"]
            a_list = [ {"sub_domain": record.sub_domain, "value": record.value,
                        "ttl": record.ttl}
                        for record in records if record.record_type.name == "A"]
            cname_list = [ {"sub_domain": record.sub_domain, "value": record.value,
                            "ttl": record.ttl} for record in records
                           if record.record_type.name == "CNAME"]
            data = {
                'soa_dict'  : soa_data,
                'ns_list'   : ns_list,
                'mx_list'   : mx_list,
                'cname_list': cname_list,
                'a_list'    : a_list
            }
            env = Environment(loader=FileSystemLoader(
                os.path.join(BASE_DIR,'template/default')),trim_blocks=True, lstrip_blocks=True)
            template = env.get_template('defaultzone.j2')
            render = template.render(**data)
            #written to the file
            zone_file = os.path.join(os.path.join(BIND_DIR,region_name),domain.name + '.zone')
            if not write_to_file(zone_file,render):
                result['error'] = '同步文件失败'
                return HttpResponse(json.dumps(result))
            #Check the configuration file syntax
            is_valid = NamedCheck()
            if not is_valid.check_zone(domain.name,zone_file):
                result['error'] = is_valid.error
                return HttpResponse(json.dumps(result))
        #reload
        for domain in all_domain:
            rndc = Named(view=region_name)
            if not rndc.reload_zone(domain.name):
                result['error'] = "reload failed"
                return HttpResponse(json.dumps(result))
        result['status'] = True
        return HttpResponse(json.dumps(result))
    except Exception as e:
        traceback.print_exc(e)
        return HttpResponse(json.dumps(result))

def sync_domain(request):
    pass










