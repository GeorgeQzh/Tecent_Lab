# -*- coding: utf-8 -*-

from django.db import models

from blueapps.account.models import User


class WeChatUser(models.Model):
    """蓝鲸账号的朋友圈资料扩展。"""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="wechat_profile")
    motto = models.CharField("个性签名", max_length=128, default="Keep learning, keep shipping.")
    pic = models.CharField("头像图片", max_length=128, default="messi.jpg")
    region = models.CharField("地区", max_length=64, default="Guangzhou")

    @property
    def email(self):
        return getattr(self.user, "email", "") or "未填写"

    def __str__(self):
        return self.user.username


class Status(models.Model):
    """朋友圈动态。"""

    user = models.ForeignKey(WeChatUser, on_delete=models.CASCADE, related_name="statuses")
    text = models.TextField("内容")
    pics = models.CharField("配图", max_length=128, blank=True, default="")
    pub_time = models.DateTimeField("发布时间", auto_now_add=True)

    class Meta:
        ordering = ("-pub_time",)
        verbose_name = "朋友圈动态"
        verbose_name_plural = verbose_name

    def __str__(self):
        return "{}: {}".format(self.user, self.text[:30])
