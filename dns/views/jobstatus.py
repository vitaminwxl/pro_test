from django.shortcuts import render_to_response
from django.template import RequestContext
from dns.models import JobStatus

def index(request, job_id):
    jobstatus = JobStatus.objects.filter(job_id=job_id)
    return render_to_response('dns/job.html', {"jobstatus": jobstatus}, context_instance=RequestContext(request))
