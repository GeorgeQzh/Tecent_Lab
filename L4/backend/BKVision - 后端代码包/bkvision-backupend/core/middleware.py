# -*- coding: utf-8 -*-

import time


class ApiRequestCollectMiddleware(object):
    """采集用户访问行为，供 BKVision 连接 SaaS 数据库后做可视化分析。"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.time()
        response = self.get_response(request)
        self._record(request, response, start)
        return response

    def _record(self, request, response, start):
        path = getattr(request, "path", "")
        if path.startswith("/static/") or path.startswith("/admin/"):
            return

        try:
            from home_application.models import ApiRequestCount

            user = getattr(request, "user", None)
            username = getattr(user, "username", "") or "anonymous"
            resolver_match = getattr(request, "resolver_match", None)
            view_name = resolver_match.url_name or resolver_match.view_name if resolver_match else ""
            x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR", "")
            ip = x_forwarded_for.split(",")[0].strip() or request.META.get("REMOTE_ADDR", "")
            ApiRequestCount.objects.create(
                username=username,
                path=path[:512],
                method=request.method,
                view_name=view_name[:128],
                status_code=getattr(response, "status_code", 200),
                cost_ms=int((time.time() - start) * 1000),
                ip=ip[:64],
                user_agent=request.META.get("HTTP_USER_AGENT", "")[:512],
            )
        except Exception:
            # 行为采集不应影响主业务请求。
            return
