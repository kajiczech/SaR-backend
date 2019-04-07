"""backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from django.conf.urls import include

from rest_framework import generics, permissions, serializers, views

from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope, TokenHasScope

from backend.core.api.LinkViewSet import LinkViewSet
from backend.core.api.GenericViewSet import GenericViewSet
from oauth2_provider import urls
from oauth2_provider import views
admin.autodiscover()





urlpatterns = [
    path('admin/', admin.site.urls),

    re_path(r'^api/', include([
        re_path(r'^(?P<version>(v1))/', include([
            re_path(r'^oauth2/', include('oauth2_provider.urls', namespace='oauth2_provider')),

            re_path(r"^oauth2/authorize$", views.AuthorizationView.as_view(), name="authorize"),
            re_path(r"^oauth2/token$", views.TokenView.as_view(), name="token"),
            re_path(r"^oauth2/revoke_token$", views.RevokeTokenView.as_view(), name="revoke-token"),
            re_path(r"^oauth2/introspect$", views.IntrospectTokenView.as_view(), name="introspect"),


            # This has to be here because the POST cannot be redirected (from endpoint without slash to endpoint with slash)

            re_path(r'^(?P<Model>[A-Za-z_-]+)/(?P<id>[0-9a-f-]+)$',
                GenericViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy', 'patch': 'patch'}, application="sar")),

            re_path(r'^(?P<Model>[A-Za-z_-]+)/(?P<id>[0-9a-f-]+)/$',
                GenericViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy', 'patch': 'patch'}, application="sar")),


            re_path(r'^(?P<Model>[A-Za-z_-]+)$',
                GenericViewSet.as_view({'get': 'list', 'post': 'create', }, application="sar")),
            re_path(r'^(?P<Model>[A-Za-z_-]+)/$',
                GenericViewSet.as_view({'get': 'list', 'post': 'create'}, application="sar")),

            re_path(
                r'^(?P<Model>[A-Za-z_-]+)/(?P<id>[0-9a-f-]+)/link/(?P<Link>[A-Za-z-_]+)$',
                LinkViewSet.as_view({'get': 'list', 'post': "add",  'delete': 'remove'},
                application="sar")
            ),

            re_path(
                r'^(?P<Model>[A-Za-z_-]+)/(?P<id>[0-9a-f-]+)/link/(?P<Link>[A-Za-z-_]+)/$',
                LinkViewSet.as_view({'get': 'list', 'post': "add", 'delete': 'remove'},
                application="sar")
            ),


        ]))
    ])),

]

