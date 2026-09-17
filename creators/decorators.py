# creators/decorators.py
from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def artisan_required(view_func):
    """
    Guard a view so only verified artisans can access it.

    Behaviour:
    - Unauthenticated users are redirected to the login page (via @login_required).
    - Authenticated users without a CreatorProfile, or with `is_verified=False`,
      receive a 403 Forbidden.
    - Verified artisans pass through. Additionally, the session's `active_role`
      is set to 'creator' so the sidebar / navigation reflects creator mode.

    Usage:
        @artisan_required
        def my_dashboard_view(request):
            ...
    """
    @wraps(view_func)
    @login_required
    def _wrapped(request, *args, **kwargs):
        profile = getattr(request.user, 'creator_profile', None)

        if not profile or not profile.is_verified:
            raise PermissionDenied(
                "You are not a verified artisan.｜您尚未成為認證匠人。"
            )

        # Force role into creator mode whenever an artisan hits their dashboard
        request.session['active_role'] = 'creator'

        return view_func(request, *args, **kwargs)

    return _wrapped


def artisan_optional(view_func):
    """
    Optional variant for views that show different content for artisans
    (e.g., a public artisan page that also displays a 'Manage' button if the
    viewer is the owner).

    Does NOT require login, and does NOT raise for non-artisans.
    The view itself is responsible for checking `request.user.creator_profile`.
    """
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        return view_func(request, *args, **kwargs)

    return _wrapped