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

from django.contrib import admin

from home_application.models import ApiRequestCount, BackupRecord, BizInfo


@admin.register(BackupRecord)
class BackupRecordAdmin(admin.ModelAdmin):
    list_display = ("bk_host_id", "bk_file_dir", "bk_file_suffix", "bk_backup_name", "bk_file_operator")
    search_fields = ("bk_host_id", "bk_file_dir", "bk_backup_name", "bk_file_operator")


@admin.register(BizInfo)
class BizInfoAdmin(admin.ModelAdmin):
    list_display = ("bk_biz_id", "bk_biz_name")
    search_fields = ("bk_biz_id", "bk_biz_name")


@admin.register(ApiRequestCount)
class ApiRequestCountAdmin(admin.ModelAdmin):
    list_display = ("username", "method", "path", "view_name", "status_code", "cost_ms", "created_at")
    search_fields = ("username", "path", "view_name")
    list_filter = ("method", "status_code", "created_at")
