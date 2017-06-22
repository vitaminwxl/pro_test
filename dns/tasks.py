from celery.decorators import task
from celery.exceptions import SoftTimeLimitExceeded
import subprocess
from dns.models import JobStatus
import time
import shlex

@task
def add(x, y):
    return x + y

@task(soft_time_limit=30)
def sync_named_conf(job_id, src="/tmp/test/", dest="/tmp/test/", slave_ip="10.69.8.43", ssh_port=22):
    jobstatus = JobStatus.objects.get(job_id=job_id, slave_ip=slave_ip)
    jobstatus.status = 1
    jobstatus.save()

    try:
        cmd = "rsync -av -e 'ssh -p %d' --delete %s %s:%s" % (ssh_port, src, slave_ip, dest)
        print cmd

        p = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        retcode = p.wait()
        (stdout, stderr) = p.communicate()
    
        print retcode
        if stdout:
            print stdout
    
        if stderr:
            print stderr
    
        if retcode != 0:
            jobstatus.status = 2
            jobstatus.save()
        else:
            jobstatus.status = 3
            jobstatus.save()
    
            restart_named_conf.delay(job_id, slave_ip, ssh_port)
    except SoftTimeLimitExceeded:
        jobstatus.status = 6
        jobstatus.save()
        
def check_job_status(job_id):
    jobstatus = JobStatus.objects.filter(job_id=job_id, status__in=[2, 5])
    return False if len(jobstatus) else True

@task(soft_time_limit=30)
def restart_named_conf(job_id, slave_ip, ssh_port):
    jobstatus = JobStatus.objects.get(job_id=job_id, slave_ip=slave_ip)

    if not check_job_status(job_id):
        jobstatus.status = 8
        jobstatus.save()
        return

    try:
        cmd = "ssh -p %d %s /etc/init.d/named restart" % (ssh_port, slave_ip)
        print cmd

        p = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        retcode = p.wait()
        (stdout, stderr) = p.communicate()
    
        print retcode
        if stdout:
            print stdout
    
        if stderr:
            print stderr
    
        if retcode != 0:
            jobstatus.status = 5
            jobstatus.save()
        else:
            jobstatus.status = 4
            jobstatus.save()

            sleep_some_seconds.delay()
    except SoftTimeLimitExceeded:
        jobstatus.status = 7
        jobstatus.save()

@task
def sleep_some_seconds(seconds=2):
    time.sleep(seconds)
