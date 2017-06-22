from dns.models import Domain, Region, Record, SOA
from jinja2 import Environment, FileSystemLoader, Template
from django.http import HttpResponse

import os

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

def preview(request, domain_name, region_name):
    domain = Domain.objects.get(name=domain_name)
    region = Region.objects.get(name=region_name)

    soa = SOA.objects.get(domain=domain)
    records = Record.objects.filter(domain=domain, region=region)
    for record in records:
        #print record.sub_domain, record.record_type, record.value, record.weight, record.mx_priority, record.ttl, record.record_type
        print record.record_type
    soa_dict = {"primary": soa.primary, "contact": soa.contact, "serial": soa.serial, "expire": soa.expire, "retry": soa.retry, "refresh": soa.refresh, "minimum": soa.minimum}
    ns_list = [ {"sub_domain": record.sub_domain, "value": record.value, "ttl": record.ttl} for record in records if record.record_type.name == "NS"]
    mx_list = [ {"sub_domain": record.sub_domain, "value": record.value, "ttl": record.ttl, "mx_priority": record.mx_priority} for record in records if record.record_type.name == "MX"]
    a_list = [ {"sub_domain": record.sub_domain, "value": record.value, "ttl": record.ttl} for record in records if record.record_type.name == "A"]
    cname_list = [ {"sub_domain": record.sub_domain, "value": record.value, "ttl": record.ttl} for record in records if record.record_type.name == "CNAME"]

    print ns_list, mx_list, a_list, cname_list

    env = Environment(loader=FileSystemLoader(
                                    os.path.join(BASE_DIR,'template/default')),
                                    trim_blocks=True, lstrip_blocks=True)
    template = env.get_template("defaultzone.j2")
    return HttpResponse(template.render(soa_dict=soa_dict, ns_list=ns_list, mx_list=mx_list, a_list=a_list, cname_list=cname_list), content_type="text/plain") 
