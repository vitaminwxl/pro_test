#coding=utf-8
from django.shortcuts import render
from django.http import HttpResponseRedirect,HttpResponse
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required

import json

@login_required(redirect_field_name='my_redirect_field')
def index(request):
    return render(request,'index.html')

def login_view(request):
    error = ''
    if request.method == 'POST':
        username = request.POST.get('username','')
        password = request.POST.get('password','')
	
	if username in ["wangxiaolong", "huzichun", "sunfeng", "zhaijianbo", "huanglingfei"]:
            user = authenticate(username=username,password=password)
            if user is not None:
                if user.is_active:
                    login(request,user)
                    return HttpResponseRedirect('/')
                else:
                    error = u'用户未启用,请联系运维同事'
            else:
                error = '用户名或者密码错误,请重新输入'
        else:
	    error = '用户名不在白名单中'
    return render(request,'login.html',locals())


def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/')
