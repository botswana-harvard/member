# coding=utf-8

from django.conf.urls import url

from .admin_site import member_admin

app_name = 'member'

urlpatterns = [
    url(r'^admin/', member_admin.urls),
]
