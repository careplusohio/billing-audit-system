from django.urls import path
from .views import (
    BillingRecordListCreateView,
    PatientListCreateView,
    ProviderListCreateView,
    AuditResultListCreateView,
    BillingCSVUploadView,
    audit_summary_stats,
    audit_results,
    export_audit_logs_csv,
    from .views import export_audit_logs_pdf
    from .views import AuditLogListView

)

urlpatterns = [
    # Core data APIs
    path('billing-records/', BillingRecordListCreateView.as_view(), name='billing-records'),
    path('patients/', PatientListCreateView.as_view(), name='patients'),
    path('providers/', ProviderListCreateView.as_view(), name='providers'),
    path('audit-results/', AuditResultListCreateView.as_view(), name='audit-results'),
    path('logs/', AuditLogListView.as_view(), name='audit-log-list'),
    path('logs/export/', export_audit_logs_csv, name='export-audit-logs'),
    path('logs/export/pdf/', export_audit_logs_pdf, name='export-audit-logs-pdf'),
    
    # CSV import and testing
    path('upload-billing-csv/', BillingCSVUploadView.as_view(), name='upload-billing-csv'),
    path('audit-results-test/', audit_results, name='audit-results-test'),

    # Dashboard stats
    path('dashboard-summary/', audit_summary_stats, name='dashboard-summary'),
]
