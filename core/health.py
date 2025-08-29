import time

from django.core.cache import cache
from django.db import connection
from django.http import JsonResponse


def health_view(request):
    """
    Comprehensive health check including database and cache connectivity.
    """
    health_data = {"status": "ok", "timestamp": time.time(), "checks": {}}
    try:
        connection["default"].cursor()
        health_data["checks"]["database"] = "ok"
    except Exception as e:
        health_data["checks"]["database"] = {"status": "error", "error": str(e)}

    try:
        cache.get("health_check")
        health_data["checks"]["cache"] = "ok"
    except Exception as e:
        health_data["checks"]["cache"] = {"status": "error", "error": str(e)}
    return JsonResponse(health_data)
