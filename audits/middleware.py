from django.shortcuts import redirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import AnonymousUser
from audits.utils import is_password_expired

class EnforcePasswordFreshnessMiddleware(MiddlewareMixin):
    def process_view(self, request, view_func, view_args, view_kwargs):
        user = request.user

        if (
            not isinstance(user, AnonymousUser)
            and user.is_authenticated
            and request.path != reverse("change-password")
            and is_password_expired(user)
        ):
            return redirect("/change-password")
