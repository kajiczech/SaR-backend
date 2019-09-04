from django.contrib import admin
from django.urls import path, re_path
from backend.core.api.endpoints import LinkEndpoint, GenericEndpoint
from backend.core.api.endpoints import MeEndpoint, RegisterUserEndpoint

admin.autodiscover()

urlpatterns = [
            re_path(r'^me$', MeEndpoint.as_view({'get': 'me'})),
            re_path(r'^me/$', MeEndpoint.as_view({'get': 'me'})),

            re_path(r'^users/register$(?i)', RegisterUserEndpoint.as_view({'post': "register_user"})),
            re_path(r'^users/register/$(?i)', RegisterUserEndpoint.as_view({'post': "register_user"})),

            # This has to be here because the POST cannot be redirected
            # (from endpoint without slash to endpoint with slash)

            re_path(r'^(?P<Model>[A-Za-z_-]+)/(?P<id>[0-9a-f-]+)$',
                GenericEndpoint.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy', 'patch': 'patch'})),

            re_path(r'^(?P<Model>[A-Za-z_-]+)/(?P<id>[0-9a-f-]+)/$',
                GenericEndpoint.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy', 'patch': 'patch'})),


            re_path(r'^(?P<Model>[A-Za-z_-]+)$',
                GenericEndpoint.as_view({'get': 'list', 'post': 'create', })),
            re_path(r'^(?P<Model>[A-Za-z_-]+)/$',
                GenericEndpoint.as_view({'get': 'list', 'post': 'create'})),

            re_path(
                r'^(?P<Model>[A-Za-z_-]+)/(?P<id>[0-9a-f-]+)/link/(?P<Link>[A-Za-z-_]+)$',
                LinkEndpoint.as_view({'get': 'list', 'post': "add",  'delete': 'remove'})
            ),

            re_path(
                r'^(?P<Model>[A-Za-z_-]+)/(?P<id>[0-9a-f-]+)/link/(?P<Link>[A-Za-z-_]+)/$',
                LinkEndpoint.as_view({'get': 'list', 'post': "add", 'delete': 'remove'})
            ),
]

