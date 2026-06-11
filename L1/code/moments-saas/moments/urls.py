# -*- coding: utf-8 -*-

from django.conf.urls import url

from moments import views


urlpatterns = (
    url(r"^$", views.homepage, name="homepage"),
    url(r"^user/?$", views.user_info, name="user_info"),
    url(r"^status/?$", views.status_list, name="status_list"),
    url(r"^post/?$", views.post_status, name="post_status"),
)
