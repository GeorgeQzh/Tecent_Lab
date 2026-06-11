# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from django.db import models


# Create your models here.


class BackupRecord(models.Model):
    """
    备份记录
    """
    bk_host_id = models.IntegerField(verbose_name="主机ID")
    bk_file_dir = models.CharField(verbose_name="备份目录", max_length=1024)
    bk_file_suffix = models.CharField(verbose_name="文件名后缀", max_length=255)
    bk_backup_name = models.CharField(verbose_name="备份文件名", max_length=1024)
    bk_file_create_time = models.CharField(verbose_name="备份时间", max_length=30)
    bk_file_operator = models.CharField(verbose_name="备份人", max_length=30)
    bk_job_link = models.CharField(verbose_name="JOB结果", max_length=100)

    class Meta:
        verbose_name = "备份记录"
        verbose_name_plural = verbose_name


class BizInfo(models.Model):
    """
    业务信息
    """

    bk_biz_id = models.IntegerField(unique=True)
    bk_biz_name = models.CharField(max_length=50)


class ApiRequestCount(models.Model):
    """
    API 请求行为记录，用于 BKVision 运营分析。
    """

    username = models.CharField("用户名", max_length=128, db_index=True)
    path = models.CharField("请求路径", max_length=512, db_index=True)
    method = models.CharField("请求方法", max_length=16)
    view_name = models.CharField("接口名称", max_length=128, blank=True, default="")
    status_code = models.IntegerField("响应状态码", default=200)
    cost_ms = models.IntegerField("耗时毫秒", default=0)
    ip = models.CharField("客户端IP", max_length=64, blank=True, default="")
    user_agent = models.CharField("User-Agent", max_length=512, blank=True, default="")
    created_at = models.DateTimeField("请求时间", auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = "API请求行为"
        verbose_name_plural = verbose_name
        ordering = ("-id",)

    def __str__(self):
        return "{} {} {}".format(self.username, self.method, self.path)
