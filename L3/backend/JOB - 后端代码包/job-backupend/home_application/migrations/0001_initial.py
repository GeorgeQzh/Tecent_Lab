# -*- coding: utf-8 -*-

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="BizInfo",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("bk_biz_id", models.IntegerField(unique=True, verbose_name="业务ID")),
                ("bk_biz_name", models.CharField(max_length=128, verbose_name="业务名称")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="更新时间")),
            ],
            options={"verbose_name": "业务信息", "verbose_name_plural": "业务信息"},
        ),
        migrations.CreateModel(
            name="BackupRecord",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("bk_host_id", models.IntegerField(verbose_name="主机ID")),
                ("bk_file_dir", models.CharField(max_length=1024, verbose_name="源文件目录")),
                ("bk_file_suffix", models.CharField(max_length=255, verbose_name="文件后缀")),
                ("bk_backup_name", models.CharField(max_length=1024, verbose_name="备份文件名")),
                ("bk_file_create_time", models.CharField(max_length=64, verbose_name="备份时间")),
                ("bk_file_operator", models.CharField(max_length=128, verbose_name="备份人")),
                ("bk_job_link", models.CharField(max_length=512, verbose_name="JOB执行结果链接")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="记录时间")),
            ],
            options={"verbose_name": "备份记录", "verbose_name_plural": "备份记录", "ordering": ("-id",)},
        ),
    ]
