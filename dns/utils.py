#Author: Wang YiChen
#coding=utf-8

from nurse import settings
from nurse.settings import logger,BIND_DIR
from jinja2 import Environment,FileSystemLoader
from dns.models import Domain,Region

import pwd
import os
import subprocess
import time
import traceback
import grp
import sys
import shlex
import socket

def chown(path, user, group=settings.group):
    if not group:
        group = user
    try:
        uid = pwd.getpwnam(user).pw_uid
        gid = grp.getgrnam(group).gr_gid
        os.chown(path, uid, gid)
    except KeyError as e:
        traceback.print_exc()
        raise KeyError('User %s does not exist'%(user))

def bash(cmd):
    """
    run a bash shell command
    执行bash命令
    """
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,shell=True)
    stdout, stderr = proc.communicate()
    if proc.returncode != 0:
        return stderr
    return proc.returncode


def mkdir(dir_name, username=settings.user, mode=settings.dir_mode):
    """
    insure the dir exist and mode ok
    目录存在，如果不存在就建立，并且权限正确
    """
    if not os.path.isdir(dir_name):
        os.makedirs(dir_name)
        os.chmod(dir_name, mode)
    if username:
        chown(dir_name, username)


def make_view_dir(view='default',username=settings.user,
                  group='',mode=settings.dir_mode,node='master'):
    """
    生成view目录
    /{{ BIND_DIR }]/master/view..
    /{{ BIND_DIR }}//slave/view..
    """
    view_dir = os.path.join(BIND_DIR,view)
    if node != 'master':
        view_dir = os.path.join(settings.slave_dir,view)
    print('view_dir',view_dir)
    if not os.path.isdir(view_dir):
        os.makedirs(view_dir)
        os.chmod(view_dir,mode)
        if group:
            chown(view_dir,username,group)
        else:
            chown(view_dir,username)

def make_zone_file(file,username=settings.user,mode=settings.file_mode):
    """
    Make Zone File
    """
    filename = os.path.join(BIND_DIR,file)

    if not os.path.exists(file):
        f = open(new_path_filename, 'w')
        f.close()
        chown(filename,username)
        os.chmod(filename,mode)

def make_file(file,username=settings.user,mode=settings.file_mode):
    """
    MakeFile
    """
    filename = os.path.join(BIND_DIR,file)
    print(filename,mode)
    if not os.path.exists(file):
        f = open(filename, 'w')
        f.close()
        chown(filename,username)
        os.chmod(filename,mode)

def backup_conf(confdir, backdir=settings.backup_dir):
    """备份named.conf和namedb目录。confdir为named配置目录， backdir为备份文件存放的目录。"""
    basename = os.path.split(confdir)[-1]
    if os.path.isdir(confdir) == False:
        return False
    else:
        time_suffix = time.strftime("%y%m%d%H%M")
        retcode = bash("tar -czf %s/%s_%s.tar.gz %s"
                                  %(backdir,basename,time_suffix,confdir))
        if retcode == 0:
            return True
    logger.error(retcode)
    return False


def write_to_file(file,data,username=settings.user,mode=settings.file_mode):
    try:
        f = open(file,'w')
        f.write(str(data))
        f.close()
        chown(file,username)
        os.chmod(file,mode)
        return True
    except Exception as e:
        logger.error(e)
        traceback.print_exc(e)
        return False

def generate_dnssec_key(keyname="test"):
    """
    :return: owner of the key
    """
    p = subprocess.Popen([settings.dnssec_keygen, "-a", "hmac-md5", "-b",
                          "128", "-n", "HOST", keyname],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    returncode = p.wait()
    (stdout, stderr) = p.communicate()
    stdout = stdout.strip()
    if returncode != 0:
        return None
    else:
        if os.path.exists(stdout+".key"):
            with open(stdout+".key") as f:
                line = f.readline()
            result = line.split()[6]

            # delete the generated key file and private file.
            os.remove(stdout+".key")
            os.remove(stdout+".private")

            return result
        else:
            return None

def render_view_all_zone_data(view,node='master'):

    """
    :param node: master/salve
    :return: 渲染view.all.zone数据
    """
    template_dir = os.path.join(settings.BASE_DIR,'dns/template/default')
    view_dir = os.path.join(BIND_DIR,view)
    if node != 'master':
        template_dir = os.path.join(settings.BASE_DIR,'dns/template/slave')
        view_dir = os.path.join(settings.slave_dir,view)
    env = Environment(loader=FileSystemLoader(template_dir),
                       trim_blocks=True, lstrip_blocks=True)
    template = env.get_template('view.all.zone')
    domains = [zone.name for zone in Domain.objects.all()]
    render_data = {
        'domains': domains,
        'view_dir': view_dir
    }
    return template.render(render_data)

def render_named_conf(node='master'):
    template_dir = os.path.join(settings.BASE_DIR,'dns/template/default')
    BIND_DIR=settings.BIND_DIR
    if node != 'master':
        template_dir = os.path.join(settings.BASE_DIR,'dns/template/slave')
        BIND_DIR = settings.slave_dir
    env = Environment(loader=FileSystemLoader(template_dir),
                   trim_blocks=True, lstrip_blocks=True)
    template_view = env.get_template('named.conf')
    views = Region.objects.all()
    render_data = {
        'views'   : views,
        'bind_dir': BIND_DIR
    }
    return template_view.render(render_data)



def remote_shell(host,port=21987):
    try:
        cmd = "ssh -p %s %s /etc/init.d/named restart" %(ssh_port,host)
        subprocess.Popen(shlex.split(cmd),stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        retcode = p.wait()
        stdout,stderr = p.communicate()
        if not retcode:
            return True
        logger.error(stdout.read() or stderr.read())
        return False
    except Exception as e:
        traceback.print_exc()
        logger.error(str(e))
        return False
