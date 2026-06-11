# -*- coding: utf-8 -*-

from django.contrib import admin

from moments.models import Status, WeChatUser


@admin.register(WeChatUser)
class WeChatUserAdmin(admin.ModelAdmin):
    list_display = ("user", "region", "motto", "pic")
    search_fields = ("user__username", "region", "motto")


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ("user", "text", "pics", "pub_time")
    list_filter = ("pub_time",)
    search_fields = ("user__user__username", "text")
