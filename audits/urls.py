# audits/urls.py
from django.urls import path, include
from .views import AuditIssueListView
from .views import update_audit_issue_status
from audits.views import audit_summary_stats
from .views import delete_patient
from .views import activity_logs_list  # ✅ THIS WAS MISSING
from . import views
from audits.views import AuditLogListView
from .views import audit_dashboard_summary
from .views import (
    audit_summary_stats,
    export_audit_logs_csv,
    export_audit_logs_pdf,
    export_audit_logs_zip,
    AuditLogListView,
    AuditIssueListView,
    export_audit_issues_csv,
    export_audit_issues_pdf,
    export_audit_issues_zip,
    admin_dashboard_summary,
    audit_issue_summary_dashboard
)

from audits.views import (
    export_audit_logs_csv,
    export_audit_logs_pdf,
    export_audit_logs_zip,
)

urlpatterns = [
    path('dashboard-summary/', audit_dashboard_summary, name='audit_dashboard_summary'),
    path("api/issues/", AuditIssueListView.as_view(), name="audit_issues_list"),
    path("api/issues/update-status/", update_audit_issue_status, name="update_audit_issue_status"),
    path("api/issues/delete-patient/", delete_patient, name="delete_patient"),
    path('api/issues/summary-dashboard/', audit_summary_stats, name='audit_summary_dashboard'),

    # ✅ CSV / PDF / ZIP Export for Issues
    path('api/issues/export/csv/', export_audit_issues_csv, name='export_audit_issues_csv'),
    path('api/issues/export/pdf/', export_audit_issues_pdf, name='export_audit_issues_pdf'),
    path('api/issues/export/zip/', export_audit_issues_zip, name='export_audit_issues_zip'),
    
    # ✅ Logs
    path('api/logs/', AuditLogListView.as_view(), name='audit_logs_list'),
   


    # ✅ CSV / PDF / ZIP Export for Logs
    path('api/logs/export/csv/', export_audit_logs_csv, name='export_audit_logs_csv'),
    path('api/logs/export/pdf/', export_audit_logs_pdf, name='export_audit_logs_pdf'),
    path('api/logs/export/zip/', export_audit_logs_zip, name='export_audit_logs_zip'),

    # ✅ This was the missing view!
    path('api/activity-logs/', activity_logs_list, name='activity_logs_list'),
    path("dashboard-summary/", admin_dashboard_summary, name="admin_dashboard_summary"),
    path("issues/summary-dashboard/", audit_issue_summary_dashboard, name="audit_issue_summary_dashboard"),
    path("activity-logs/", AuditLogListView.as_view(), name="activity_logs"),

    path("export/csv/", export_audit_logs_csv, name="export_logs_csv"),
    path("export/pdf/", export_audit_logs_pdf, name="export_logs_pdf"),
    path("export/zip/", export_audit_logs_zip, name="export_logs_zip"),
    path("audit-summary/", audit_summary_stats, name="audit-summary"),
]
