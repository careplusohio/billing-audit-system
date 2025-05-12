from django.urls import path
from .views import (
    ProviderListView, ProviderDetailView, ProviderUpdateView,
    export_provider_pdf, export_providers_pdf, export_providers_csv, export_providers_zip
)

urlpatterns = [
    path('', ProviderListView.as_view(), name='provider_list'),
    path('<int:id>/', ProviderDetailView.as_view(), name='provider_detail'),
    path('<int:id>/edit/', ProviderUpdateView.as_view(), name='provider_edit'),

    # ✅ Export endpoints (must match exactly)
    path('export/pdf/', export_providers_pdf, name='export_providers_pdf'),
    path('export/csv/', export_providers_csv, name='export_providers_csv'),
    path('export/zip/', export_providers_zip, name='export_providers_zip'),
    path('<int:id>/export/pdf/', export_provider_pdf, name='export_provider_pdf'),
]
