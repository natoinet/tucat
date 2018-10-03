# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView
from django.views.defaults import bad_request, permission_denied, page_not_found, server_error
from django.views.static import serve

#import private_storage.urls


urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='pages/home.html'), name="home"),
    url(r'^about/$', TemplateView.as_view(template_name='pages/about.html'), name="about"),

    # Django Admin
    url(r'^admin/', admin.site.urls),

    # User management
    #url(r'^users/', include("tucat.users.urls", namespace="users")),
    url(r'^users/', include("tucat.users.urls")),
    url(r'^accounts/', include('allauth.urls')),
    #url('^private-media/', include(private_storage.urls)),

    #url(r'^media/(?P<path>.*)$', serve({'document_root': settings.MEDIA_ROOT})),


] #+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) #+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)# + static(settings.OUTPUT_URL, document_root=settings.STATIC_ROOT)

admin.site.site_header = 'Tucat Administration'
admin.site.site_title = 'Tucat Administration'
admin.site.index_title = 'Home'
