# -*- coding: utf-8 -*-

import json
import time

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET

from blueking.component.shortcuts import get_client_by_request
from home_application.constants import (
    BACKUP_FILE_PLAN_ID,
    BK_JOB_HOST,
    JOB_BK_BIZ_ID,
    JOB_RESULT_ATTEMPTS_INTERVAL,
    MAX_ATTEMPTS,
    SEARCH_FILE_PLAN_ID,
    SUCCESS_CODE,
    WAITING_CODE,
    WEB_SUCCESS_CODE,
)
from home_application.models import BackupRecord, BizInfo


def home(request):
    """首页。"""

    return render(request, "home_application/index_home.html")


def dev_guide(request):
    """开发指引。"""

    return render(request, "home_application/dev_guide.html")


def contact(request):
    """联系页。"""

    return render(request, "home_application/contact.html")


def _int_arg(request, name):
    value = request.GET.get(name)
    if value in (None, ""):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _json_error(message, code=400, data=None):
    return JsonResponse(
        {"result": False, "code": code, "message": message, "data": data or {}},
        status=code,
    )


def _host_ids(request):
    raw = request.GET.get("host_id_list", "")
    try:
        host_ids = [int(item) for item in raw.split(",") if item.strip()]
    except ValueError:
        host_ids = []
    return host_ids


def _job_link(job_instance_id):
    return "{}/biz/{}/execute/task/{}".format(BK_JOB_HOST.rstrip("/"), JOB_BK_BIZ_ID, job_instance_id)


def _wait_job_success(client, job_instance_id):
    kwargs = {
        "bk_scope_type": "biz",
        "bk_scope_id": JOB_BK_BIZ_ID,
        "job_instance_id": job_instance_id,
    }
    last_status = None
    for _ in range(MAX_ATTEMPTS):
        result = client.jobv3.get_job_instance_status(kwargs)
        if not result.get("result"):
            return False, result.get("message", "get job status failed"), None

        step_list = result.get("data", {}).get("step_instance_list") or []
        if not step_list:
            return False, "empty step instance list", None

        step = step_list[0]
        last_status = step.get("status")
        if last_status == SUCCESS_CODE:
            return True, "", step.get("step_instance_id")
        if last_status != WAITING_CODE:
            return False, "job failed, status={}".format(last_status), step.get("step_instance_id")
        time.sleep(JOB_RESULT_ATTEMPTS_INTERVAL)
    return False, "job timeout, last status={}".format(last_status), None


def _read_host_log(client, job_instance_id, step_instance_id, bk_host_id):
    result = client.jobv3.get_job_instance_ip_log(
        {
            "bk_scope_type": "biz",
            "bk_scope_id": JOB_BK_BIZ_ID,
            "job_instance_id": job_instance_id,
            "step_instance_id": step_instance_id,
            "bk_host_id": bk_host_id,
        }
    )
    if not result.get("result"):
        return {"bk_host_id": bk_host_id, "message": result.get("message", "get log failed")}

    data = result.get("data") or {}
    content = data.get("log_content") or "{}"
    try:
        parsed = json.loads(content)
    except (TypeError, ValueError):
        parsed = {"message": content}

    if isinstance(parsed, dict):
        parsed["bk_host_id"] = data.get("bk_host_id", bk_host_id)
        return parsed
    return [{"bk_host_id": data.get("bk_host_id", bk_host_id), **item} for item in parsed]


@require_GET
def get_bizs_list(request):
    """获取 CMDB 业务列表，并缓存到本地数据库。"""

    bizs = BizInfo.objects.order_by("bk_biz_id")
    if bizs.exists() and request.GET.get("refresh") != "1":
        return JsonResponse(
            {
                "result": True,
                "code": WEB_SUCCESS_CODE,
                "data": {"count": bizs.count(), "info": list(bizs.values("bk_biz_id", "bk_biz_name"))},
            }
        )

    client = get_client_by_request(request)
    result = client.cc.search_business(
        {
            "fields": ["bk_biz_id", "bk_biz_name"],
            "page": {"start": 0, "limit": 100, "sort": "bk_biz_id"},
        }
    )
    if result.get("result") and result.get("data"):
        for biz in result["data"].get("info", []):
            BizInfo.objects.update_or_create(
                bk_biz_id=biz["bk_biz_id"],
                defaults={"bk_biz_name": biz["bk_biz_name"]},
            )
    return JsonResponse(result)


@require_GET
def get_sets_list(request):
    """根据业务 ID 查询集群列表。"""

    bk_biz_id = _int_arg(request, "bk_biz_id")
    if not bk_biz_id:
        return _json_error("bk_biz_id is required")

    client = get_client_by_request(request)
    return JsonResponse(
        client.cc.search_set(
            {
                "bk_biz_id": bk_biz_id,
                "fields": ["bk_set_id", "bk_set_name", "bk_biz_id", "bk_created_at", "bk_supplier_account"],
                "page": {"start": 0, "limit": 500, "sort": "bk_set_id"},
            }
        )
    )


@require_GET
def get_modules_list(request):
    """根据业务 ID 和集群 ID 查询模块列表。"""

    bk_biz_id = _int_arg(request, "bk_biz_id")
    bk_set_id = _int_arg(request, "bk_set_id")
    if not bk_biz_id or not bk_set_id:
        return _json_error("bk_biz_id and bk_set_id are required")

    client = get_client_by_request(request)
    return JsonResponse(
        client.cc.search_module(
            {
                "bk_biz_id": bk_biz_id,
                "bk_set_id": bk_set_id,
                "fields": ["bk_module_id", "bk_module_name", "bk_set_id", "bk_biz_id", "bk_created_at"],
                "page": {"start": 0, "limit": 500, "sort": "bk_module_id"},
            }
        )
    )


@require_GET
def get_hosts_list(request):
    """查询主机列表，支持拓扑与主机属性筛选。"""

    bk_biz_id = _int_arg(request, "bk_biz_id") or JOB_BK_BIZ_ID
    kwargs = {
        "bk_biz_id": bk_biz_id,
        "page": {"start": 0, "limit": 100},
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
    for arg_name, field_name in (
        ("bk_host_name", "bk_host_name"),
        ("bk_host_innerip", "bk_host_innerip"),
        ("operator", "operator"),
        ("bk_bak_operator", "bk_bak_operator"),
    ):
        value = request.GET.get(arg_name)
        if value:
            rules.append({"field": field_name, "operator": "contains", "value": value.strip()})
    if rules:
        kwargs["host_property_filter"] = {"condition": "AND", "rules": rules}

    client = get_client_by_request(request)
    return JsonResponse(client.cc.list_biz_hosts(kwargs))


@require_GET
def get_host_detail(request):
    """查询主机详情。"""

    bk_host_id = _int_arg(request, "bk_host_id")
    if not bk_host_id:
        return _json_error("bk_host_id is required")
    client = get_client_by_request(request)
    return JsonResponse(client.cc.get_host_base_info({"bk_host_id": bk_host_id}))


@require_GET
def search_file(request):
    """通过 JOB 执行方案查询主机文件。"""

    host_ids = _host_ids(request)
    if not host_ids:
        return _json_error("host_id_list is required")
    if not request.GET.get("search_path") or not request.GET.get("suffix"):
        return _json_error("search_path and suffix are required")

    client = get_client_by_request(request)
    result = client.jobv3.execute_job_plan(
        {
            "bk_scope_type": "biz",
            "bk_scope_id": JOB_BK_BIZ_ID,
            "job_plan_id": SEARCH_FILE_PLAN_ID,
            "global_var_list": [
                {"name": "host_list", "server": {"host_id_list": host_ids}},
                {"name": "search_path", "value": request.GET.get("search_path")},
                {"name": "suffix", "value": request.GET.get("suffix")},
            ],
        }
    )
    if not result.get("result"):
        return JsonResponse(result)

    job_instance_id = result.get("data", {}).get("job_instance_id")
    ok, message, step_instance_id = _wait_job_success(client, job_instance_id)
    if not ok:
        return _json_error(message, data={"job_instance_id": job_instance_id})

    logs = [_read_host_log(client, job_instance_id, step_instance_id, host_id) for host_id in host_ids]
    return JsonResponse({"result": True, "code": WEB_SUCCESS_CODE, "data": logs})


@require_GET
def backup_file(request):
    """通过 JOB 执行方案备份文件，并写入备份记录。"""

    host_ids = _host_ids(request)
    search_path = request.GET.get("search_path")
    suffix = request.GET.get("suffix")
    backup_path = request.GET.get("backup_path")
    if not host_ids:
        return _json_error("host_id_list is required")
    if not search_path or not suffix or not backup_path:
        return _json_error("search_path, suffix and backup_path are required")

    client = get_client_by_request(request)
    result = client.jobv3.execute_job_plan(
        {
            "bk_scope_type": "biz",
            "bk_scope_id": JOB_BK_BIZ_ID,
            "job_plan_id": BACKUP_FILE_PLAN_ID,
            "global_var_list": [
                {"name": "host_list", "server": {"host_id_list": host_ids}},
                {"name": "search_path", "value": search_path},
                {"name": "suffix", "value": suffix},
                {"name": "backup_path", "value": backup_path},
            ],
        }
    )
    if not result.get("result"):
        return JsonResponse(result)

    job_instance_id = result.get("data", {}).get("job_instance_id")
    ok, message, step_instance_id = _wait_job_success(client, job_instance_id)
    if not ok:
        return _json_error(message, data={"job_instance_id": job_instance_id})

    username = getattr(request.user, "username", "") or "unknown"
    created = []
    for host_id in host_ids:
        host_log = _read_host_log(client, job_instance_id, step_instance_id, host_id)
        log_items = host_log if isinstance(host_log, list) else [host_log]
        for item in log_items:
            if item.get("message"):
                continue
            record = BackupRecord.objects.create(
                bk_host_id=host_id,
                bk_file_dir=search_path,
                bk_file_suffix=suffix,
                bk_backup_name=item.get("bk_backup_name") or item.get("backup_name") or backup_path,
                bk_file_create_time=item.get("bk_file_create_time") or item.get("create_time") or "",
                bk_file_operator=username,
                bk_job_link=_job_link(job_instance_id),
            )
            created.append(record.id)

    return JsonResponse(
        {
            "result": True,
            "code": WEB_SUCCESS_CODE,
            "data": {"job_instance_id": job_instance_id, "record_ids": created},
        }
    )


@require_GET
def get_backup_record(request):
    """查询备份记录。"""

    records = BackupRecord.objects.all().order_by("-id").values(
        "id",
        "bk_host_id",
        "bk_file_dir",
        "bk_file_suffix",
        "bk_backup_name",
        "bk_file_create_time",
        "bk_file_operator",
        "bk_job_link",
        "created_at",
    )
    return JsonResponse({"result": True, "code": WEB_SUCCESS_CODE, "data": list(records)})
