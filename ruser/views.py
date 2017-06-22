#coding=utf-8
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.models import User
from ruser.models import User
from django.contrib.auth.decorators import login_required
from nurse.settings import logger


import json

# Create your views here.

@login_required(login_url='/login')
def user_add(request):
    result = {'status':False,'error':''}
    if request.method == 'POST':
        username = request.POST.get('username','')
        email = request.POST.get('email','')
        role = request.POST.get('role','')
        memo = request.POST.get('memo','')
        tel = request.POST.get('tel','')


        required = filter(lambda i: i.strip('') == '',[username,email,role])
        if required:
            result['error'] = 'This value [{0}] is required.'.format(required)
            return HttpResponse(json.dumps(request))
        add_info = {
            'username': username,
            'email': email,
            'tel' : tel,
            'role': role,
        }
        try:
            add_user = User(**add_info)
            add_user.save()
            logger.info('added user:[{0}],email:[{1}],role:[{2}],tel:[{3}]'
                        .format(username,email,role,tel))
        except Exception as e:
            logger.debug(str(e))
        result['status'] = True
        return HttpResponse(json.dumps(request))
    return render(request,'ruser/user_add.html')


def user_del(request,uid):
    result = {'status':False,'error':''}
    try:
        del_user = User.objects.get(id=uid).delete()

    except Exception as e:
        logger.debug(str(e))
        result['error'] = 'User does not exist.'
        return HttpResponse(json.dumps(result))
    result['status'] = True
    return HttpResponse(json.dumps(result))

def user_list(request):
    try:
        user_list = User.objects.all()
    except Exception as e:
        logger.debug(str(e))

    render(request,'ruser/user_list.html',locals())

def user_edit(request,uid):
    """
    :param request: user_info = [{},{}]
    :param uid:
    :return:
    """
    if request.method == 'POST':
        result = {'status':False,'error':''}

        info = json.dumps(request.POST.get('user_info'))
        if not info:
            result['error'] = 'Data is empty'
            return HttpResponse(json.dumps(result))
        try:
            for item in info:
                user_obj = User.objects.get(item['id'])
                for keys in item:
                    user_obj.keys = item(keys)
                user_obj.save()
            result['status'] = True
        except Exception as e:
            logger.debug(str(e))
            result['error'] = '服务内部错误.'
            return HttpResponse(json.dumps(result))

        return HttpResponse(json.dumps(result))





