from django.urls import path
from .views import (
    PatientListView,
    PatientDetailView,
    PatientUpdateView,
    patients_list,
    export_patients_pdf,
    export_patients_csv,
    export_patients_zip,
)

urlpatterns = [
    path("", PatientListView.as_view(), name="patient-list"),
    path("<int:id>/", PatientDetailView.as_view(), name="patient-detail"),
    path("<int:id>/edit/", PatientUpdateView.as_view(), name="patient-update"),
    path("test/", patients_list, name="patients-test"),
    path("export/pdf/", export_patients_pdf, name="export-patients-pdf"),
    path("export/csv/", export_patients_csv, name="export-patients-csv"),
    path("export/zip/", export_patients_zip, name="export-patients-zip"),
]
