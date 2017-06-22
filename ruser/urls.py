from django.conf.urls import include,url
import views

urlpatterns = [
    url(r'^user_add/$', views.user_add, name='user_add'),
    url(r'^user_del/(?P<uid>\d+)/$', views.user_del,name='user_del'),
    url(r'^user_edit/(?P<uid>\d+)/$', views.user_edit, name='user_edit'),
    url(r'^user_list/$',views.user_list,name='user_list')
]