from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

# ✅ Simple test endpoint to confirm routing
def test_api(request):
    return JsonResponse({"message": "✅ backend.urls is working"})

urlpatterns = [
    path('admin/', admin.site.urls),

    # ✅ API endpoints grouped cleanly
    path('api/', include('billing.urls')),              # /api/...
    path('api/patients/', include('patients.urls')),    # /api/patients/...
    path('api/providers/', include('providers.urls')),  # /api/providers/...
    path('api/audits/', include('audits.urls')),        # /api/audits/...

    # ✅ Auth endpoints
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # ✅ Test API endpoint
    path('api/test/', test_api, name='api_test'),
]
