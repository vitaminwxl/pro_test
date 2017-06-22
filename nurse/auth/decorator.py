#Author: Wang YiChen
#coding=utf-8
from django.http import HttpResponseRedirect,HttpResponse

def permission(role='CU'):
    def _deco(func):
        def __deco(request,*args,**kwargs):
            request.session['pre_url'] = request.path
            if not request.user.is_authenticated():
                return HttpResponseRedirect('/login')
            if role == 'CU':
                if request.user.role_type in ['CU','SU']:
                    return func(request,*args,**kwargs)
            elif role == 'SU':
                if request.user.role_type in ['SU']:
                    return func(request,*args,**kwargs)
            else:
                return HttpResponse('Permission denied')
        return __deco
    return _deco




