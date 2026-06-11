# -*- coding: utf-8 -*-

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="BackupRecord",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("bk_host_id", models.IntegerField(verbose_name="主机ID")),
                ("bk_file_dir", models.CharField(max_length=1024, verbose_name="备份目录")),
                ("bk_file_suffix", models.CharField(max_length=255, verbose_name="文件名后缀")),
                ("bk_backup_name", models.CharField(max_length=1024, verbose_name="备份文件名")),
                ("bk_file_create_time", models.CharField(max_length=30, verbose_name="备份时间")),
                ("bk_file_operator", models.CharField(max_length=30, verbose_name="备份人")),
                ("bk_job_link", models.CharField(max_length=100, verbose_name="JOB结果")),
            ],
            options={"verbose_name": "备份记录", "verbose_name_plural": "备份记录"},
        ),
        migrations.CreateModel(
            name="BizInfo",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("bk_biz_id", models.IntegerField(unique=True)),
                ("bk_biz_name", models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name="ApiRequestCount",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("username", models.CharField(db_index=True, max_length=128, verbose_name="用户名")),
                ("path", models.CharField(db_index=True, max_length=512, verbose_name="请求路径")),
                ("method", models.CharField(max_length=16, verbose_name="请求方法")),
                ("view_name", models.CharField(blank=True, default="", max_length=128, verbose_name="接口名称")),
                ("status_code", models.IntegerField(default=200, verbose_name="响应状态码")),
                ("cost_ms", models.IntegerField(default=0, verbose_name="耗时毫秒")),
                ("ip", models.CharField(blank=True, default="", max_length=64, verbose_name="客户端IP")),
                ("user_agent", models.CharField(blank=True, default="", max_length=512, verbose_name="User-Agent")),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True, verbose_name="请求时间")),
            ],
            options={"verbose_name": "API请求行为", "verbose_name_plural": "API请求行为", "ordering": ("-id",)},
        ),
    ]
