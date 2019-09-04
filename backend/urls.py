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
from backend.core.api import authorization
from oauth2_provider import views


admin.autodiscover()

urlpatterns = [
    path('admin/', admin.site.urls),

    re_path(r'^api/', include([
        re_path(r'^(?P<version>(v1))/', include([
            re_path(r'^oauth2/', include('oauth2_provider.urls', namespace='oauth2_provider')),

            re_path(r"^oauth2/authorize$", views.AuthorizationView.as_view(), name="authorize"),
            re_path(r"^oauth2/token$", authorization.TokenView.as_view(), name="token"),
            re_path(r"^oauth2/revoke_token$", views.RevokeTokenView.as_view(), name="revoke-token"),
            re_path(r"^oauth2/introspect$", views.IntrospectTokenView.as_view(), name="introspect"),
            re_path("", include('backend.core.urls')),
        ]))
    ])),

]

