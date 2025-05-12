# /backend/api/urls.py
from django.urls import path, include
from authentication.views import CustomTokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    # 🔐 Authentication
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # 🧾 Audit Log Activity & Summary
    path("logs/", include("audits.urls")),               # ✅ For /api/logs/...
    path("audits/", include("audits.urls_audit")), 
          # ✅ This file DOES exist
       # ✅ For /api/audits/...

    # 💳 Billing & Rhino
    path("billing/", include("billing.urls")),
    path("billing/rhino/", include("audits.urls_rhino")),

    # 🧑‍⚕️ Patient Endpoints
    path("patients/", include("patients.urls")),

    # 🧾 Legacy fallback (optional)
    path("", include("billing.urls")),
]
