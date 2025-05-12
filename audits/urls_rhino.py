from django.urls import path
from audits.views import BillingCSVUploadView

urlpatterns = [
    path("upload/", BillingCSVUploadView.as_view(), name="upload_rhino_csv"),
]