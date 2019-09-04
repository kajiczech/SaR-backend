from django.contrib import admin
from django.urls import path, re_path

from backend.apps.sar.api import authorization

admin.autodiscover()

urlpatterns = [
            re_path(r"^oauth2/token$", authorization.TokenView.as_view(), name="token"),
            re_path(r"^oauth2/token/$", authorization.TokenView.as_view(), name="token"),
]

