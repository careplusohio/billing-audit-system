from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.models import User
from django.contrib.auth import views as auth_views

# ✅ Custom serializer to support login via username or email
class UsernameOrEmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        login = attrs.get("username")  # may be username or email
        password = attrs.get("password")

        try:
            # Try login with username first
            user = User.objects.get(username=login)
        except User.DoesNotExist:
            # Fallback: try login with email
            try:
                user = User.objects.get(email=login)
            except User.DoesNotExist:
                raise serializers.ValidationError("Invalid username or email")

        attrs["username"] = user.username  # required by TokenObtainPairSerializer
        return super().validate(attrs)

# ✅ Use the serializer in a custom token view
class CustomTokenView(TokenObtainPairView):
    serializer_class = UsernameOrEmailTokenObtainPairSerializer

# ✅ Optional test endpoint
def test_api_root(request):
    return JsonResponse({"message": "✅ API root is working!"})

# ✅ Final URL patterns
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('audits.urls')),
    path('api/', include('billing.urls')),

    # JWT login endpoint (supports email or username)
    path('api/token/', CustomTokenView.as_view(), name='token_obtain_pair'),

    # Password reset routes
    path('api/password-reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('api/password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
]
