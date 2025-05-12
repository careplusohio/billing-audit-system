from django.urls import path
from .views import VisitListView, VisitCreateView, VisitDetailView, VisitUpdateView
from .views import export_visits_pdf, export_visits_csv, export_visits_zip

urlpatterns = [
    path("", VisitListView.as_view()),
    path("add/", VisitCreateView.as_view()),
    path("<int:pk>/", VisitDetailView.as_view()),
    path("<int:pk>/edit/", VisitUpdateView.as_view()),
    path("<int:id>/delete/", delete_visit, name="delete_visit"),
    path("export/pdf/", export_visits_pdf, name="export_visits_pdf"),
    path("export/csv/", export_visits_csv, name="export_visits_csv"),
    path("export/zip/", export_visits_zip, name="export_visits_zip"),
    path("", VisitListCreateView.as_view(), name="visit-list"),

]
