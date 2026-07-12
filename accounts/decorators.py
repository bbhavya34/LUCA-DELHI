from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


def role_required(role):
    def decorator(view):
        @login_required
        @wraps(view)
        def wrapped(request, *args, **kwargs):
            user = request.user
            if not user.is_account_active or not user.is_active:
                messages.error(request, "Your account has been disabled.")
                return redirect("accounts:logout")
            if not (user.role == role or (role == "ADMIN" and user.is_superuser)):
                messages.error(request, "You are not authorised to access that page.")
                return redirect("dashboard:redirect")
            return view(request, *args, **kwargs)
        return wrapped
    return decorator


admin_required = role_required("ADMIN")
member_required = role_required("MEMBER")
