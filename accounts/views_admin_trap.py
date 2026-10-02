# accounts/views_admin_trap.py
import logging

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .models import AdminTrapHit
from .utils import client_ip

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["GET", "POST"])
def fake_admin_login(request):
    """
    Honeypot for the real Django admin.
    Every hit is logged; nothing useful is ever served.
    """
    ip = client_ip(request)
    ua = request.META.get("HTTP_USER_AGENT", "")[:300]
    method = request.method

    submitted_username = ""
    submitted_password_present = False
    if method == "POST":
        submitted_username = request.POST.get("username", "")[:100]
        submitted_password_present = bool(request.POST.get("password"))

    logger.warning(
        "ADMIN_TRAP_HIT | ip=%s | method=%s | path=%s | ua=%s | username=%r | pwd_present=%s",
        ip, method, request.path, ua, submitted_username, submitted_password_present,
    )

    try:
        AdminTrapHit.objects.create(
            ip=ip,
            user_agent=ua,
            path=request.path[:255],
            method=method,
            submitted_username=submitted_username,
            submitted_password_present=submitted_password_present,
        )
    except Exception:
        # The trap must never break — a failed log is acceptable.
        logger.exception("Failed to persist AdminTrapHit")

    return render(
        request,
        "accounts/admin_trap.html",
        {"page_title": "Sign in｜登入", "submitted_username": submitted_username},
        status=200,
    )