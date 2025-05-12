from django.http import JsonResponse, HttpResponse
from rest_framework.generics import ListAPIView, RetrieveAPIView, UpdateAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from weasyprint import HTML
from .models import Patient
from authentication.serializers import PatientSerializer
import csv
from io import BytesIO, TextIOWrapper
from zipfile import ZipFile
from audits.utils import log_action


class PatientListView(ListAPIView):
    queryset = Patient.objects.all().order_by("last_name")
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ["first_name", "last_name", "insurance_id", "payer"]


class PatientDetailView(RetrieveAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"


class PatientUpdateView(UpdateAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def perform_update(self, serializer):
        patient = serializer.save()
        user = self.request.user
        log_action(user, "update", f"Updated patient: {patient.first_name} {patient.last_name}")


class PatientCreateView(CreateAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        patient = serializer.save()
        user = self.request.user
        log_action(user, "create", f"Created patient: {patient.first_name} {patient.last_name}")


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_patient(request, id):
    patient = get_object_or_404(Patient, id=id)
    full_name = f"{patient.first_name} {patient.last_name}"
    patient.delete()
    log_action(request.user, "delete", f"Deleted patient: {full_name}")
    return Response({"message": "Patient deleted successfully."})


def patients_list(request):
    return JsonResponse({"message": "✅ Patients endpoint is working"})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def export_patients_pdf(request):
    patients = Patient.objects.all().order_by("last_name")
    html = render_to_string("pdf/patient_list_pdf.html", {"patients": patients})
    pdf = HTML(string=html, base_url=request.build_absolute_uri()).write_pdf()
    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = 'inline; filename="patients_list.pdf"'
    return response


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def export_patients_csv(request):
    patients = Patient.objects.all().order_by("last_name")
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="patients_list.csv"'

    writer = csv.writer(response)
    writer.writerow(["First Name", "Last Name", "Gender", "DOB", "Insurance ID", "Payer"])
    for p in patients:
        writer.writerow([
            p.first_name,
            p.last_name,
            p.gender,
            p.dob,
            p.insurance_id,
            p.payer,
        ])
    return response


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def export_patients_zip(request):
    patients = Patient.objects.all().order_by("last_name")
    buffer = BytesIO()
    zip_file = ZipFile(buffer, "w")

    # CSV Part
    csv_io = TextIOWrapper(BytesIO(), encoding="utf-8", newline="")
    writer = csv.writer(csv_io)
    writer.writerow(["First Name", "Last Name", "Gender", "DOB", "Insurance ID", "Payer"])
    for p in patients:
        writer.writerow([
            p.first_name,
            p.last_name,
            p.gender,
            p.dob,
            p.insurance_id,
            p.payer,
        ])
    csv_io.seek(0)
    zip_file.writestr("patients.csv", csv_io.read())

    # PDF Part
    html = render_to_string("pdf/patient_list_pdf.html", {"patients": patients})
    pdf = HTML(string=html, base_url=request.build_absolute_uri()).write_pdf()
    zip_file.writestr("patients.pdf", pdf)

    zip_file.close()
    buffer.seek(0)
    response = HttpResponse(buffer, content_type="application/zip")
    response["Content-Disposition"] = 'attachment; filename="patients_export.zip"'
    return response
