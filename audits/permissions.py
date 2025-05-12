from rest_framework.permissions import BasePermission
from rest_framework_simplejwt.authentication import JWTAuthentication
from .utils import is_password_expired  # ✅ Correct relative import



class RequireFreshPassword(BasePermission):
    """
    Denies access if the user's password is expired (older than X days).
    """
    def has_permission(self, request, view):
        return not is_password_expired(request.user)


class IsAdminUserFromJWT(BasePermission):
    """
    Allows access only to users with 'admin' role embedded in their JWT token.
    """
    def has_permission(self, request, view):
        auth = JWTAuthentication()
        header = auth.get_header(request)
        if header is None:
            return False

        raw_token = auth.get_raw_token(header)
        if raw_token is None:
            return False

        try:
            validated_token = auth.get_validated_token(raw_token)
        except Exception:
            return False

        role = validated_token.get("role", None)
        return role == "admin"
