# accounts/decorators.py
from functools import wraps
from django.core.exceptions import PermissionDenied


def superuser_required(view_func):
    """
    Require an authenticated user with Account.is_superadmin=True.
    Raises PermissionDenied (403) otherwise.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied
        if not getattr(request.user, "is_superadmin", False):
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapper