from django.urls import path, include
from .views import billing_records  # ✅ This should exist in views.py
from .views import BillingRecordDetailView, BillingRecordUpdateView
from .views import export_billing_csv, export_billing_pdf, export_billing_zip
from .views import billing_summary, billing_weekly_stats
from .views import billing_summary_dashboard, billing_weekly_stats

from .views import delete_billing_record
from .views import (
    dashboard_summary_stats,
    billing_weekly_stats,
    audit_summary_stats,
)

urlpatterns = [
    path('billing-records/', billing_records),
    path('billing-records/<int:id>/', BillingRecordDetailView.as_view(), name='billing_record_detail'),
    path('billing-records/<int:id>/edit/', BillingRecordUpdateView.as_view(), name='billing_record_update'),
    path('billing-records/export/csv/', export_billing_csv, name='export_billing_csv'),
    path('billing-records/export/pdf/', export_billing_pdf, name='export_billing_pdf'),
    path('billing-records/export/zip/', export_billing_zip, name='export_billing_zip'),
    path('billing-records/<int:id>/delete/', delete_billing_record, name='billing_record_delete'),
    path('dashboard-summary/', dashboard_summary_stats, name='dashboard_summary'),
    path('billing-weekly-stats/', billing_weekly_stats, name='billing_weekly_stats'),
    path('rhino/', include('audits.urls_rhino')),  # ✅ THIS IS REQUIRED
    path('dashboard-summary/', dashboard_summary_stats, name='dashboard_summary'),
    path('audit-summary/', audit_summary_stats, name='audit_summary'),
    path("dashboard-summary/", billing_summary_dashboard, name="billing_summary_dashboard"),
    path("billing-weekly-stats/", billing_weekly_stats, name="billing_weekly"),
    

]
