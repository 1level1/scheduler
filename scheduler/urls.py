'''
Created on Feb 12, 2018

@author: lkuznets
'''
from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from django.urls import include, path# new
from . import views

urlpatterns = [
    url(r'^interns/$', views.InternsList.as_view()),
    url(r'^roles/$', views.RoleList.as_view()),
    url(r'^department/$', views.DepartmentView.as_view()),
    url(r'^department_interns/(?P<pk>[0-9]+)/$', views.DepartmentInternsList.as_view()),
    url(r'^department_roles/(?P<pk>[0-9]+)/$', views.DepartmentRoles.as_view()),
    url(r'^intern_roles/(?P<pk>[0-9]+)/$', views.InternRoles.as_view()),
    url(r'^intern_schedule/(?P<pk>[0-9]+)/$', views.InternScheduleLimitations.as_view()),
    url(r'^duty_limit_type/$', views.DutyLimitView.as_view()),
    url(r'^create_schedule/(?P<pk>[0-9]+)/$', views.SchedulerView.as_view()),
    path('accounts/', include('django.contrib.auth.urls')),
]

urlpatterns = format_suffix_patterns(urlpatterns)