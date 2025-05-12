from django.urls import path
from . import views
from .views import audit_summary_stats

urlpatterns = [
    path("audit-summary/", views.audit_summary_dashboard, name="audit_summary"),
    path("summary/", views.audit_summary_stats, name="audit_summary_stats"),
    path("issues/", views.AuditIssueListView.as_view(), name="audit_issues"),
    path("issues/export/csv/", views.export_audit_issues_csv),
    path("issues/export/pdf/", views.export_audit_issues_pdf),
    path("issues/export/zip/", views.export_audit_issues_zip),
    path("audit-summary/", audit_summary_stats, name="audit_summary_stats"),
]