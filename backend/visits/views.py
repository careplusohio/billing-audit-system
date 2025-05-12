from django.template.loader import render_to_string
from weasyprint import HTML
from io import BytesIO, TextIOWrapper
import csv
from zipfile import ZipFile
from django.http import HttpResponse
from .models import Visit

# ✅ /billing-audit-system/backend/visits/views.py

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def export_visits_pdf(request):
    visits = Visit.objects.all().order_by("-visit_date", "-visit_time")
    html = render_to_string("pdf/visit_list_pdf.html", {"visits": visits})
    pdf = HTML(string=html, base_url=request.build_absolute_uri()).write_pdf()
    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = 'inline; filename="visits_list.pdf"'
    return response

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def export_visits_csv(request):
    visits = Visit.objects.all().order_by("-visit_date", "-visit_time")
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="visits_list.csv"'

    writer = csv.writer(response)
    writer.writerow(["Visit Date", "Visit Time", "Patient", "Provider", "Notes"])
    for visit in visits:
        writer.writerow([
            visit.visit_date,
            visit.visit_time,
            str(visit.patient),
            str(visit.provider),
            visit.notes,
        ])
    return response

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def export_visits_zip(request):
    visits = Visit.objects.all().order_by("-visit_date", "-visit_time")
    buffer = BytesIO()
    zip_file = ZipFile(buffer, "w")

    # CSV Part
    csv_io = TextIOWrapper(BytesIO(), encoding="utf-8", newline="")
    writer = csv.writer(csv_io)
    writer.writerow(["Visit Date", "Visit Time", "Patient", "Provider", "Notes"])
    for visit in visits:
        writer.writerow([
            visit.visit_date,
            visit.visit_time,
            str(visit.patient),
            str(visit.provider),
            visit.notes,
        ])
    csv_io.seek(0)
    zip_file.writestr("visits.csv", csv_io.read())

    # PDF Part
    html = render_to_string("pdf/visit_list_pdf.html", {"visits": visits})
    pdf = HTML(string=html, base_url=request.build_absolute_uri()).write_pdf()
    zip_file.writestr("visits.pdf", pdf)

    zip_file.close()
    buffer.seek(0)
    response = HttpResponse(buffer.read(), content_type="application/zip")
    response["Content-Disposition"] = 'attachment; filename="visits_export.zip"'
    return response
