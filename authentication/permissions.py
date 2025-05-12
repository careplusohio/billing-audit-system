# /billing-audit-system/authentication/permissions.py

from rest_framework.permissions import BasePermission
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed

class IsAdminUserFromJWT(BasePermission):
    def has_permission(self, request, view):
        auth = JWTAuthentication()
        try:
            validated_token = auth.get_validated_token(auth.get_raw_token(request.headers.get('Authorization').split()[1]))
            user = auth.get_user(validated_token)
            return user.is_staff  # or check your custom role
        except Exception:
            raise AuthenticationFailed('Invalid token or not authorized.')

class RequireFreshPassword(BasePermission):
    def has_permission(self, request, view):
        # Example: Allow all for now; you can improve it later
        return True
