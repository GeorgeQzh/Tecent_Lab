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

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET

from blueking.component.shortcuts import get_client_by_request

from home_application.models import BizInfo


# 开发框架中通过中间件默认是需要登录态的，如有不需要登录的，可添加装饰器login_exempt
# 装饰器引入 from blueapps.account.decorators import login_exempt
def home(request):
    """
    首页
    """
    return render(request, "home_application/index_home.html")


def dev_guide(request):
    """
    开发指引
    """
    return render(request, "home_application/dev_guide.html")


def contact(request):
    """
    联系页
    """
    return render(request, "home_application/contact.html")


def _int_arg(request, name):
    value = request.GET.get(name)
    if value in (None, ""):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _page(request):
    current = max(_int_arg(request, "page") or 1, 1)
    limit = min(max(_int_arg(request, "limit") or 20, 1), 100)
    return {"start": (current - 1) * limit, "limit": limit}


def _json_error(message, code=400):
    return JsonResponse({"result": False, "code": code, "message": message, "data": {}}, status=code)


@require_GET
def get_bizs_list(request):
    """
    获取业务列表
    """
    cached = BizInfo.objects.order_by("bk_biz_id")
    if cached.exists() and request.GET.get("refresh") != "1":
        return JsonResponse(
            {
                "result": True,
                "code": 0,
                "data": {"count": cached.count(), "info": list(cached.values("bk_biz_id", "bk_biz_name"))},
            }
        )

    # 从环境配置获取 APP 信息，从 request 获取当前用户信息
    client = get_client_by_request(request)
    kwargs = {
        "fields": [
            "bk_biz_id",
            "bk_biz_name"
        ],
        # 社区版环境中业务数量有限，先不考虑分页情况
        "page": {
            "start": 0,
            "limit": 15,
            "sort": ""
        }
    }
    result = client.cc.search_business(kwargs)
    if result.get("result") and result.get("data"):
        for biz in result["data"].get("info", []):
            BizInfo.objects.update_or_create(
                bk_biz_id=biz["bk_biz_id"],
                defaults={"bk_biz_name": biz["bk_biz_name"]},
            )
    return JsonResponse(result)


@require_GET
def get_sets_list(request):
    """
    根据业务ID，查询业务下的集群列表
    """
    bk_biz_id = _int_arg(request, "bk_biz_id")
    if not bk_biz_id:
        return _json_error("bk_biz_id is required")

    client = get_client_by_request(request)
    kwargs = {
        "bk_biz_id": bk_biz_id,
        "fields": ["bk_set_id", "bk_set_name", "bk_biz_id", "bk_created_at", "bk_supplier_account"],
        "page": {"start": 0, "limit": 500, "sort": "bk_set_id"},
    }
    return JsonResponse(client.cc.search_set(kwargs))


@require_GET
def get_modules_list(request):
    """
    根据业务ID和集群ID，查询对应的模块列表
    """
    bk_biz_id = _int_arg(request, "bk_biz_id")
    bk_set_id = _int_arg(request, "bk_set_id")
    if not bk_biz_id or not bk_set_id:
        return _json_error("bk_biz_id and bk_set_id are required")

    client = get_client_by_request(request)
    kwargs = {
        "bk_biz_id": bk_biz_id,
        "bk_set_id": bk_set_id,
        "fields": ["bk_module_id", "bk_module_name", "bk_set_id", "bk_biz_id", "bk_created_at", "bk_supplier_account"],
        "page": {"start": 0, "limit": 500, "sort": "bk_module_id"},
    }
    return JsonResponse(client.cc.search_module(kwargs))


@require_GET
def get_hosts_list(request):
    """
    根据传递的查询条件，包括但不限于（业务ID、集群ID、模块ID、主机ID、主机维护人）
    查询主机列表
    """
    bk_biz_id = _int_arg(request, "bk_biz_id")
    if not bk_biz_id:
        return _json_error("bk_biz_id is required")

    kwargs = {
        "bk_biz_id": bk_biz_id,
        "page": _page(request),
        "fields": [
            "bk_host_id",
            "bk_host_name",
            "bk_cloud_id",
            "bk_host_innerip",
            "bk_os_name",
            "bk_os_type",
            "bk_mac",
            "operator",
            "bk_bak_operator",
        ],
    }

    bk_set_id = _int_arg(request, "bk_set_id")
    if bk_set_id:
        kwargs["bk_set_ids"] = [bk_set_id]

    bk_module_id = _int_arg(request, "bk_module_id")
    if bk_module_id:
        kwargs["bk_module_ids"] = [bk_module_id]

    rules = []
    fuzzy_fields = {
        "bk_host_name": "bk_host_name",
        "bk_host_innerip": "bk_host_innerip",
        "operator": "operator",
        "bk_bak_operator": "bk_bak_operator",
    }
    for arg_name, field_name in fuzzy_fields.items():
        value = request.GET.get(arg_name) or request.GET.get("host_ip" if arg_name == "bk_host_innerip" else arg_name)
        if value:
            rules.append({"field": field_name, "operator": "contains", "value": value.strip()})

    bk_host_id = _int_arg(request, "bk_host_id")
    if bk_host_id:
        rules.append({"field": "bk_host_id", "operator": "equal", "value": bk_host_id})

    if rules:
        kwargs["host_property_filter"] = {"condition": "AND", "rules": rules}

    client = get_client_by_request(request)
    result = client.cc.list_biz_hosts(kwargs)
    if result.get("result") and result.get("data"):
        result["data"].setdefault("count", len(result["data"].get("info", [])))
    return JsonResponse(result)


@require_GET
def get_host_detail(request):
    """
    根据主机ID，查询主机详情信息
    """
    bk_host_id = _int_arg(request, "bk_host_id")
    if not bk_host_id:
        return _json_error("bk_host_id is required")

    client = get_client_by_request(request)
    result = client.cc.get_host_base_info({"bk_host_id": bk_host_id})
    return JsonResponse(result)
