#coding=utf-8
from django.conf.urls import url, patterns
from dns.views import views,record, preview,sync, jobstatus
 
urlpatterns = [
    url(r'^$', record.index, name='index'),
    url(r'^domain_show/$',record.domain_show,name='domain_show'),
    url(r'^domain_add/$',record.domain_add,name='domain_add'),
    url(r'^domain_delete/(?P<domain_id>\d+)/$',record.domain_delete,name='domain_delete'),
    url(r'^acl_list/$',record.acl_list,name='acl_list'),
    url(r'^acl_add/$',record.acl_add,name='acl_add'),
]

urlpatterns += [
    url(r'^view/show$',views.view_show,name='view_show'),
    url(r'^view/add$',views.view_add,name='view_add'),
    url(r'^view/del/(?P<view_id>\d+)/$',views.view_delete,name='view_delete'),
 ]

urlpatterns += [
    url(r'^record_add/$',record.record_add,name='record_add'),
    url(r'^record_show/(?P<domain_id>\d+)/$',record.record_show,name='record_show'),
    url(r'^record_edit/$',record.record_edit,name='record_edit'),
    url(r'^record_del/$',record.record_del,name='record_del'),
 ]

urlpatterns += [
    url(r'^preview/(?P<domain_name>.*)/(?P<region_name>.*)/', preview.preview, name="preview")
]

urlpatterns += [
    url(r'^sync/$',sync.sync_record,name='sync_record'),
    url(r'^sync_view/(?P<view_id>\d+)/$',sync.sync_view,name='sync_view'),
]
 
urlpatterns += [
    #url(r'^job/(?P<job_id>[a-f0-9-]+)/$', jobstatus.index)
    url(r'^job/(?P<job_id>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/$',jobstatus.index)
]
