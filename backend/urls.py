from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.conf import settings
from audits.views import update_audit_issue_status
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from audits.views import audit_summary_stats
from billing.views import dashboard_summary_stats
from billing.views import billing_weekly_stats, dashboard_summary_stats
from audits.views import audit_summary_stats

def test_api(request):
    return JsonResponse({"message": "✅ backend.urls is working"})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('authentication.urls')),
    path('api/billing/', include('billing.urls')),
    path('api/core/', include('coreapi.urls')),
    path('api/', include('backend.api.urls')),
    path('api/patients/', include('patients.urls')),
    path('api/providers/', include('backend.providers.urls')),
    path('api/audits/', include('audits.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/test/', test_api, name='api_test'),
    path('issues/<int:id>/update-status/', update_audit_issue_status, name="update_audit_issue_status"),
    path('api/dashboard-summary/', dashboard_summary_stats, name="dashboard_summary"),
    path('api/billing-weekly-stats/', billing_weekly_stats, name="billing_weekly_stats"),
    path('api/audit-summary/', audit_summary_stats, name="audit_summary_stats"),


    # ❌ Removed the duplicate billing include
    # path("api/", include("billing.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
