# ✅ /billing-audit-system/billing/views.py

from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q
from django.utils.dateparse import parse_date
from zipfile import ZipFile
from io import TextIOWrapper, BytesIO
import csv
from weasyprint import HTML
from django.db.models.functions import TruncWeek
from billing.models import BillingRecord, Patient, Provider

from audits.models import AuditResult
from billing.models import AuditLog
from django.db.models import Sum, Count
from datetime import timedelta, date
from django.utils import timezone
from .models import BillingRecord
from .serializers import (
    PatientSerializer,
    ProviderSerializer,
    BillingRecordSerializer,
)
from audits.serializers import (
    AuditResultSerializer,
    AuditLogSerializer,
)

from rest_framework.generics import RetrieveAPIView, UpdateAPIView


class BillingRecordDetailView(RetrieveAPIView):
    queryset = BillingRecord.objects.all()
    serializer_class = BillingRecordSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

class BillingRecordUpdateView(UpdateAPIView):
    queryset = BillingRecord.objects.all()
    serializer_class = BillingRecordSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

def billing_records(request):
    return JsonResponse({"message": "Billing records endpoint is working ✅"})

def filter_logs_by_date(queryset, request):
    start = request.GET.get("start")
    end = request.GET.get("end")
    if start:
        start_date = parse_date(start)
        if start_date:
            queryset = queryset.filter(timestamp__date__gte=start_date)
    if end:
        end_date = parse_date(end)
        if end_date:
            queryset = queryset.filter(timestamp__date__lte=end_date)
    return queryset

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def audit_summary_stats(request):
    data = {
        "total_patients": Patient.objects.count(),
        "total_providers": Provider.objects.count(),
        "total_audits": AuditResult.objects.count(),
        "total_records": BillingRecord.objects.count(),
        "total_issues": AuditResult.objects.count(),
        "open_issues": AuditResult.objects.filter(status="Open").count(),
        "resolved_issues": AuditResult.objects.filter(status="Resolved").count(),
    }
    return Response(data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_audit_logs_csv(request):
    logs = filter_logs_by_date(AuditLog.objects.all(), request)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="audit_logs.csv"'
    writer = csv.writer(response)
    writer.writerow(['Timestamp', 'Action', 'User', 'Details'])
    for log in logs:
        writer.writerow([
            log.timestamp,
            log.action_type,
            log.user,
            log.description
        ])
    return response

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_audit_logs_pdf(request):
    logs = filter_logs_by_date(AuditLog.objects.all(), request)
    html_string = render_to_string('audit_logs_pdf.html', {
        'logs': logs,
        'start': request.GET.get("start", ""),
        'end': request.GET.get("end", ""),
    })
    pdf_file = HTML(string=html_string).write_pdf()
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="audit_logs.pdf"'
    return response

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_audit_logs_zip(request):
    logs = filter_logs_by_date(AuditLog.objects.all(), request)
    buffer = BytesIO()
    zip_file = ZipFile(buffer, 'w')

    # CSV
    csv_buffer = BytesIO()
    csv_writer = csv.writer(TextIOWrapper(csv_buffer, encoding='utf-8', newline=''))
    csv_writer.writerow(['Timestamp', 'Action', 'User', 'Details'])
    for log in logs:
        csv_writer.writerow([log.timestamp, log.action_type, log.user, log.description])
    csv_buffer.seek(0)
    zip_file.writestr("audit_logs.csv", csv_buffer.read())

    # PDF
    html_string = render_to_string('audit_logs_pdf.html', {
        'logs': logs,
        'start': request.GET.get("start", ""),
        'end': request.GET.get("end", ""),
    })
    pdf_content = HTML(string=html_string).write_pdf()
    zip_file.writestr("audit_logs.pdf", pdf_content)

    zip_file.close()
    buffer.seek(0)
    response = HttpResponse(buffer.read(), content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename="audit_logs.zip"'
    return response

class AuditLogListView(generics.ListAPIView):
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = AuditLog.objects.all().order_by('-timestamp')
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(user__icontains=search) |
                Q(action_type__icontains=search)
            )
        return filter_logs_by_date(queryset, self.request)

class BillingRecordListCreateView(generics.ListCreateAPIView):
    queryset = BillingRecord.objects.all()
    serializer_class = BillingRecordSerializer

class PatientListCreateView(generics.ListCreateAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer

class ProviderListCreateView(generics.ListCreateAPIView):
    queryset = Provider.objects.all()
    serializer_class = ProviderSerializer

class AuditResultListCreateView(generics.ListCreateAPIView):
    queryset = AuditResult.objects.all()
    serializer_class = AuditResultSerializer

class BillingCSVUploadView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request, format=None):
        file_obj = request.FILES.get("file")
        if not file_obj:
            return Response({"error": "No file uploaded"}, status=400)

        csv_file = TextIOWrapper(file_obj.file, encoding='utf-8')
        reader = csv.DictReader(csv_file)
        imported = 0
        errors = []

        for row in reader:
            try:
                patient, _ = Patient.objects.get_or_create(
                    first_name=row["first_name"],
                    last_name=row["last_name"],
                    defaults={"dob": "1990-01-01", "gender": "Other", "insurance_id": "000", "payer": row["payer"]}
                )
                provider, _ = Provider.objects.get_or_create(
                    provider_name=row["provider_name"],
                    defaults={"npi": "0000", "certification": "Test", "compliance_status": "Active"}
                )
                record = BillingRecord.objects.create(
                    patient=patient,
                    provider=provider,
                    payer=row["payer"],
                    service_date=row["service_date"],
                    service_code=row["service_code"],
                    diagnosis_code=row["diagnosis_code"],
                    units=int(row["units"]),
                    amount_billed=float(row["amount_billed"]),
                    allowed_amount=float(row["allowed_amount"]),
                    paid_amount=float(row["paid_amount"]),
                    billing_status=row.get("billing_status", "Submitted"),
                )
                if record.amount_billed > record.allowed_amount:
                    AuditResult.objects.create(
                        billing_record=record,
                        issue_type="Rate Discrepancy",
                        description="Amount billed exceeds allowed rate.",
                        status="Open",
                    )
                imported += 1
            except Exception as e:
                errors.append(str(e))

        return Response({
            "imported": imported,
            "errors": errors
        }, status=201)

# ✅ New billing export views
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def export_billing_csv(request):
    records = BillingRecord.objects.all().order_by("-created_at")
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="billing_records.csv"'

    writer = csv.writer(response)
    writer.writerow(["Visit ID", "Service Code", "Amount", "Paid", "Created At"])
    for record in records:
        writer.writerow([
            record.visit.id if record.visit else "",
            record.service_code,
            record.amount_billed,
            "Yes" if record.paid_amount > 0 else "No",
            record.created_at,
        ])
    return response

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def export_billing_pdf(request):
    records = BillingRecord.objects.all().order_by("-created_at")
    html = render_to_string("pdf/billing_list_pdf.html", {"records": records})
    pdf = HTML(string=html, base_url=request.build_absolute_uri()).write_pdf()
    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = 'inline; filename="billing_records.pdf"'
    return response

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def export_billing_zip(request):
    records = BillingRecord.objects.all().order_by("-created_at")
    buffer = BytesIO()
    zip_file = ZipFile(buffer, "w")

    csv_io = TextIOWrapper(BytesIO(), encoding="utf-8", newline="")
    writer = csv.writer(csv_io)
    writer.writerow(["Visit ID", "Service Code", "Amount", "Paid", "Created At"])
    for record in records:
        writer.writerow([
            record.visit.id if record.visit else "",
            record.service_code,
            record.amount_billed,
            "Yes" if record.paid_amount > 0 else "No",
            record.created_at,
        ])
    csv_io.seek(0)
    zip_file.writestr("billing_records.csv", csv_io.read())

    html = render_to_string("pdf/billing_list_pdf.html", {"records": records})
    pdf_bytes = HTML(string=html, base_url=request.build_absolute_uri()).write_pdf()
    zip_file.writestr("billing_records.pdf", pdf_bytes)

    zip_file.close()
    buffer.seek(0)
    response = HttpResponse(buffer.read(), content_type="application/zip")
    response["Content-Disposition"] = 'attachment; filename="billing_records_export.zip"'
    return response

@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_billing_record(request, id):
    record = get_object_or_404(BillingRecord, id=id)
    summary = f"Billing Record for Visit ID {record.visit.id} - Service Code {record.service_code}"
    record.delete()
    return Response({"message": f"{summary} deleted successfully."}, status=status.HTTP_200_OK)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard_summary_stats(request):
    total_billing = BillingRecord.objects.aggregate(total=Sum("amount_billed"))["total"] or 0
    total_paid = BillingRecord.objects.aggregate(paid=Sum("paid_amount"))["paid"] or 0
    unpaid = total_billing - total_paid

    summary = {
        "total_records": BillingRecord.objects.count(),
        "total_amount_billed": total_billing,
        "total_paid_amount": total_paid,
        "total_unpaid_amount": unpaid,
        "total_patients": Patient.objects.count(),
        "total_providers": Provider.objects.count(),
    }
    return Response(summary)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def billing_summary(request):
    total_billed = BillingRecord.objects.aggregate(total=Sum("amount_billed"))["total"] or 0
    total_paid = BillingRecord.objects.aggregate(total=Sum("paid_amount"))["total"] or 0
    total_allowed = BillingRecord.objects.aggregate(total=Sum("allowed_amount"))["total"] or 0
    total_records = BillingRecord.objects.count()

    return Response({
        "total_billed": total_billed,
        "total_paid": total_paid,
        "total_allowed": total_allowed,
        "total_records": total_records
    })

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def billing_weekly_stats(request):
    today = date.today()
    six_weeks_ago = today - timedelta(weeks=6)

    weekly_stats = (
        BillingRecord.objects.filter(service_date__gte=six_weeks_ago)
        .annotate(week=TruncWeek("service_date"))
        .values("week")
        .annotate(total_billed=Sum("amount_billed"))
        .order_by("week")
    )

    return Response(list(weekly_stats))

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def billing_summary_dashboard(request):
    total_billed = BillingRecord.objects.aggregate(total=Sum("amount_billed"))["total"] or 0
    total_paid = BillingRecord.objects.aggregate(total=Sum("paid_amount"))["total"] or 0
    total_allowed = BillingRecord.objects.aggregate(total=Sum("allowed_amount"))["total"] or 0
    total_records = BillingRecord.objects.count()

    return Response({
        "total_billed": total_billed,
        "total_paid": total_paid,
        "total_allowed": total_allowed,
        "total_records": total_records
    })
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def audit_summary(request):
    return Response({
        "total_issues": AuditResult.objects.count(),
        "open_issues": AuditResult.objects.filter(status="Open").count(),
        "resolved_issues": AuditResult.objects.filter(status="Resolved").count(),
        "total_records": BillingRecord.objects.count()
    })
