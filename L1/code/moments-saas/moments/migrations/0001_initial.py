# -*- coding: utf-8 -*-

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("account", "__first__"),
    ]

    operations = [
        migrations.CreateModel(
            name="WeChatUser",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("motto", models.CharField(default="Keep learning, keep shipping.", max_length=128, verbose_name="个性签名")),
                ("pic", models.CharField(default="messi.jpg", max_length=128, verbose_name="头像图片")),
                ("region", models.CharField(default="Guangzhou", max_length=64, verbose_name="地区")),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="wechat_profile",
                        to="account.user",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Status",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("text", models.TextField(verbose_name="内容")),
                ("pics", models.CharField(blank=True, default="", max_length=128, verbose_name="配图")),
                ("pub_time", models.DateTimeField(auto_now_add=True, verbose_name="发布时间")),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="statuses",
                        to="moments.wechatuser",
                    ),
                ),
            ],
            options={
                "verbose_name": "朋友圈动态",
                "verbose_name_plural": "朋友圈动态",
                "ordering": ("-pub_time",),
            },
        ),
    ]
