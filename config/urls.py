"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views.
"""

from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse

from . import views


urlpatterns = [

    path('', views.home, name='home'),

    path('admin/', admin.site.urls),

    path('accounts/', include('accounts.urls')),

    path('profiles/', include('profiles.urls')),

    path('matching/', include('matching.urls')),

    path('requests/', include('requests_app.urls')),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )