"""member URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url

from edc_constants.constants import UUID_PATTERN

from household.patterns import household_identifier
from plot.patterns import plot_identifier
from survey.patterns import survey_schedule

from .admin_site import member_admin
from .views import ListboardView, AnonymousListboardView

app_name = 'member'


def listboard_urls():
    urlpatterns = []
    listboard_configs = [
        ('listboard_url', ListboardView, 'listboard'),
        ('anonymous_listboard_url', AnonymousListboardView, 'anonymous_listboard')]

    for listboard_url_name, listboard_view_class, label in listboard_configs:
        urlpatterns.extend([
            url(r'^' + label + '/'
                '(?P<household_identifier>' + household_identifier + ')/'
                '(?P<survey_schedule>' + survey_schedule + ')/'
                '(?P<page>\d+)/',
                listboard_view_class.as_view(), name=listboard_url_name),
            url(r'^' + label + '/'
                '(?P<household_identifier>' + household_identifier + ')/'
                '(?P<survey_schedule>' + survey_schedule + ')/',
                listboard_view_class.as_view(), name=listboard_url_name),
            url(r'^' + label + '/'
                '(?P<household_identifier>' + household_identifier + ')/',
                listboard_view_class.as_view(), name=listboard_url_name),
            url(r'^' + label + '/'
                '(?P<plot_identifier>' + plot_identifier + ')/'
                '(?P<survey_schedule>' + survey_schedule + ')/',
                listboard_view_class.as_view(), name=listboard_url_name),
            url(r'^' + label + '/'
                '(?P<plot_identifier>' + plot_identifier + ')/',
                listboard_view_class.as_view(), name=listboard_url_name),
            url(r'^' + label + '/'
                '(?P<id>' + UUID_PATTERN.pattern + ')/',
                listboard_view_class.as_view(), name=listboard_url_name),
            url(r'^' + label + '/'
                '(?P<page>\d+)/',
                listboard_view_class.as_view(), name=listboard_url_name),
            url(r'^' + label + '/',
                listboard_view_class.as_view(), name=listboard_url_name),
        ])
    return urlpatterns


urlpatterns = [url(r'^admin/', member_admin.urls)] + listboard_urls()
