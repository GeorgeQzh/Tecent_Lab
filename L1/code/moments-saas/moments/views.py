# -*- coding: utf-8 -*-

from django.conf import settings
from django.shortcuts import redirect, render

from moments.models import Status, WeChatUser


def _static_url():
    return getattr(settings, "BK_STATIC_URL", getattr(settings, "STATIC_URL", "/static")).rstrip("/")


def _site_url():
    return getattr(settings, "SITE_URL", "/").rstrip("/") or ""


def _context(**extra):
    data = {"BK_STATIC_URL": _static_url(), "SITE_URL": _site_url()}
    data.update(extra)
    return data


def _current_wechat_user(request):
    profile, _ = WeChatUser.objects.get_or_create(
        user=request.user,
        defaults={
            "motto": "BlueKing SaaS developer",
            "pic": "messi.jpg",
            "region": "Guangzhou",
        },
    )
    return profile


def homepage(request):
    return render(request, "homepage.html", _context())


def user_info(request):
    return render(request, "user.html", _context(user=_current_wechat_user(request)))


def status_list(request):
    return render(request, "status.html", _context(statuses=Status.objects.select_related("user", "user__user")))


def post_status(request):
    profile = _current_wechat_user(request)
    if request.method == "POST":
        text = request.POST.get("text", "").strip()
        if text:
            Status.objects.create(user=profile, text=text)
        return redirect("{}{}".format(_site_url(), "/status"))
    return render(request, "my_post.html", _context(user=profile))
