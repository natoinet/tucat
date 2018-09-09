# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView
from django.views.defaults import bad_request, permission_denied, page_not_found, server_error

urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='pages/home.html'), name="home"),
    url(r'^about/$', TemplateView.as_view(template_name='pages/about.html'), name="about"),

    # Django Admin
    url(r'^admin/', admin.site.urls),

    # User management
    #url(r'^users/', include("tucat.users.urls", namespace="users")),
    url(r'^users/', include("tucat.users.urls")),
    url(r'^accounts/', include('allauth.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
