
from audits.models import AuditActivityLog, AuditIssue
from django.shortcuts import render
from django.utils import timezone
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from django.db.models import Q
from django.utils.dateparse import parse_date
from zipfile import ZipFile
from io import TextIOWrapper, BytesIO
import csv

from rest_framework.generics import ListAPIView
from authentication.permissions import IsAdminUserFromJWT  # already used in your app
from billing.models import BillingRecord, Patient, Provider
from .models import AuditResult
from billing.models import AuditLog
from audits.utils import log_action
from rest_framework import status
from audits.models import AuditIssueHistory   # ✅ Added
from audits.models import AuditResult
from patients.models import Patient

from .serializers import AuditActivityLogSerializer
from .serializers import (
    BillingRecordSerializer,
    PatientSerializer,
    ProviderSerializer,
    AuditResultSerializer,
    AuditLogSerializer,
)
from audits.permissions import IsAdminUserFromJWT, RequireFreshPassword
from audits.serializers import AuditLogSerializer

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
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def admin_dashboard_summary(request):
    total_records = AuditResult.objects.count()
    open_issues = AuditResult.objects.filter(status="Open").count()
    resolved_issues = AuditResult.objects.filter(status="Resolved").count()

    return Response({
        "total_records": total_records,
        "open_issues": open_issues,
        "resolved_issues": resolved_issues
    })

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def audit_issue_summary_dashboard(request):
    return Response({
        "total_issues": 15,
        "open_issues": 9,
        "resolved_issues": 6
    })
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def audit_dashboard_summary(request):
    from audits.models import AuditIssue  # import inside to avoid circular import

    total_issues = AuditIssue.objects.count()
    open_issues = AuditIssue.objects.filter(status='Open').count()
    resolved_issues = AuditIssue.objects.filter(status='Resolved').count()

    return Response({
        "total_issues": total_issues,
        "open_issues": open_issues,
        "resolved_issues": resolved_issues
    })

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
def audit_results(request):
    return Response({
        "message": "This is a test endpoint for audit results.",
        "status": "success"
    })

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
def export_audit_logs_csv(request):
    logs = filter_logs_by_date(AuditLog.objects.all(), request)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="audit_logs.csv"'
    writer = csv.writer(response)
    writer.writerow(['Timestamp', 'Action', 'User', 'Details'])
    for log in logs:
        writer.writerow([
            log.timestamp,
            log.action,
            log.user.email if log.user else '',
            log.details
        ])
    return response

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_audit_logs_zip(request):
    logs = filter_logs_by_date(AuditLog.objects.all(), request)

    buffer = BytesIO()
    zip_file = ZipFile(buffer, 'w')

    # CSV
    csv_buffer = TextIOWrapper(BytesIO(), encoding='utf-8', newline='')
    writer = csv.writer(csv_buffer)
    writer.writerow(['Timestamp', 'Action', 'User', 'Details'])
    for log in logs:
        writer.writerow([
            log.timestamp,
            log.action,
            log.user.email if log.user else '',
            log.details
        ])
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

    response = HttpResponse(buffer, content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename="audit_logs.zip"'
    return response
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_patient(request, id):
    try:
        patient = Patient.objects.get(id=id)
        patient_name = patient.name  # or whatever field represents the name
        patient.delete()

        # ✅ Log the deletion into AuditLog
        AuditLog.objects.create(
            user=request.user,
            action_type="DELETE",
            description=f"Deleted patient: {patient_name} (ID {id})",
            timestamp=timezone.now()
        )

        return Response({"message": "Patient deleted and logged successfully."}, status=status.HTTP_204_NO_CONTENT)
    except Patient.DoesNotExist:
        return Response({"error": "Patient not found."}, status=status.HTTP_404_NOT_FOUND)
        
class AuditLogListView(generics.ListAPIView):
    queryset = AuditLog.objects.all().order_by("-timestamp")
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated]


class BillingRecordListCreateView(generics.ListCreateAPIView):
    queryset = BillingRecord.objects.all()
    serializer_class = BillingRecordSerializer

class PatientListCreateView(generics.ListCreateAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer

class ProviderListCreateView(generics.ListCreateAPIView):
    queryset = Provider.objects.all()
    serializer_class = ProviderSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        provider = serializer.save()
        user = self.request.user
        log_action(user, "Add Provider", f"Provider {provider.provider_name} was added.")

class AuditResultListCreateView(generics.ListCreateAPIView):
    queryset = AuditResult.objects.all()
    serializer_class = AuditResultSerializer

class AuditIssueListView(generics.ListAPIView):
    queryset = AuditResult.objects.all()
    serializer_class = AuditResultSerializer
    permission_classes = [IsAuthenticated]


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

# 🔥 Helper function for audit flags
def detect_audit_flags(record):
    flags = []

    # 1. High Amount
    if record.amount_billed > 5000:
        flags.append("High Amount")

    # 2. Late Submission
    if (record.service_date and record.billing_status.lower() == "submitted"):
        days_late = (timezone.now().date() - record.service_date).days
        if days_late > 30:
            flags.append("Late Submission")

    # 3. Duplicate Entry
    duplicate = BillingRecord.objects.filter(
        patient=record.patient,
        service_date=record.service_date
    ).exclude(id=record.id).exists()
    if duplicate:
        flags.append("Duplicate Entry")

    # 4. Missing Diagnosis Code
    if not record.diagnosis_code or record.diagnosis_code.strip() == "":
        flags.append("Missing Diagnosis Code")

    # 5. Unusual Service Duration (Example > 12 units)
    if record.units > 12:
        flags.append("Unusual Service Duration")

    return flags

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

                # ✅ Detect audit flags
                flags = detect_audit_flags(record)

                issue_type = "General Audit Issue"
                description = "Automatic audit check applied."
                if record.amount_billed > record.allowed_amount:
                    issue_type = "Rate Discrepancy"
                    description = "Amount billed exceeds allowed rate."

                # ✅ Save AuditResult with flags
                AuditResult.objects.create(
                    billing_record=record,
                    issue_type=issue_type,
                    description=description,
                    status="Open",
                    flags=", ".join(flags) if flags else None
                )

                imported += 1
            except Exception as e:
                errors.append(str(e))

        return Response({
            "imported": imported,
            "errors": errors
        }, status=201)

# =======================
# 🚀 Audit Issues Exports
# =======================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_audit_issues_csv(request):
    issues = AuditResult.objects.all()

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="audit_issues.csv"'
    writer = csv.writer(response)
    writer.writerow(['Patient', 'Issue Type', 'Description', 'Flags', 'Status', 'Review Date'])

    for issue in issues:
        patient = str(issue.billing_record.patient) if issue.billing_record else "—"
        writer.writerow([
            patient,
            issue.issue_type,
            issue.description,
            issue.flags or "",
            issue.status,
            issue.review_date.strftime("%Y-%m-%d") if issue.review_date else ""
        ])


  

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_audit_issues_pdf(request):
    issues = AuditResult.objects.all()

    html_string = render_to_string('audit_issues_pdf.html', {
        'issues': issues
    })
    pdf_file = HTML(string=html_string).write_pdf()

    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="audit_issues.pdf"'
    return response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_audit_issues_zip(request):
    issues = AuditResult.objects.all()
    buffer = BytesIO()
    zip_file = ZipFile(buffer, 'w')

    # CSV part
    csv_buffer = TextIOWrapper(BytesIO(), encoding='utf-8', newline='')
    writer = csv.writer(csv_buffer)
    writer.writerow(['Patient', 'Issue Type', 'Description', 'Flags', 'Status', 'Review Date'])
    for issue in issues:
        patient = str(issue.billing_record.patient) if issue.billing_record else "—"
        writer.writerow([
            patient,
            issue.issue_type,
            issue.description,
            issue.flags or "",
            issue.status,
            issue.review_date.strftime("%Y-%m-%d") if issue.review_date else ""
        ])
    csv_buffer.seek(0)
    zip_file.writestr("audit_issues.csv", csv_buffer.read())

    # PDF part
    html_string = render_to_string('audit_issues_pdf.html', {
        'issues': issues
    })
    pdf_content = HTML(string=html_string).write_pdf()
    zip_file.writestr("audit_issues.pdf", pdf_content)

    zip_file.close()
    buffer.seek(0)

    response = HttpResponse(buffer, content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename="audit_issues.zip"'
    return response



@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_audit_issue_status(request, id):
    try:
        issue = AuditResult.objects.get(id=id)
        new_status = request.data.get("status")
        if new_status not in ["Open", "Resolved"]:
            return Response({"error": "Invalid status."}, status=400)

        old_status = issue.status

        if old_status != new_status:
            # Save the history before changing the status
            AuditIssueHistory.objects.create(
                issue=issue,
                changed_by=request.user,
                old_status=old_status,
                new_status=new_status
            )

            issue.status = new_status
            issue.save()

        return Response({"message": "Status updated successfully."})

    except AuditResult.DoesNotExist:
        return Response({"error": "Issue not found."}, status=404)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def audit_summary_dashboard(request):
    # Issues per month
    issues_by_month = AuditResult.objects.annotate(
        month=TruncMonth('review_date')
    ).values('month').annotate(count=Count('id')).order_by('month')

    issues_per_month = {
        str(item['month'].strftime("%Y-%m")): item['count']
        for item in issues_by_month if item['month']
    }

    # Flags distribution
    all_issues = AuditResult.objects.all()
    flag_counts = {}
    for issue in all_issues:
        flags = issue.flags.split(',') if issue.flags else []
        for flag in flags:
            flag = flag.strip()
            if flag:
                flag_counts[flag] = flag_counts.get(flag, 0) + 1

    # Status counts
    status_counts = AuditResult.objects.values('status').annotate(count=Count('id'))
    status_data = {item['status']: item['count'] for item in status_counts}

    # ✅ Activity log (cleaned)
    

    return Response({
        "issues_per_month": issues_per_month,
        "flags_distribution": flag_counts,
        "status_counts": status_data
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def activity_logs_list(request):
    logs = filter_logs_by_date(AuditActivityLog.objects.all(), request)
    serializer = AuditActivityLogSerializer(logs, many=True)  # ✅ Correct serializer
    return Response(serializer.data)


def apply_activity_log_filters(queryset, request):
    start = request.GET.get('start')
    end = request.GET.get('end')
    action_type = request.GET.get('action_type')
    user = request.GET.get('user')
    search = request.GET.get('search')

    if start and end:
        queryset = queryset.filter(timestamp__range=[start, end])
    if action_type:
        queryset = queryset.filter(action_type__icontains=action_type)
    if user:
        queryset = queryset.filter(user__email__icontains=user)
    if search:
        queryset = queryset.filter(description__icontains=search)

    return queryset

# ========== ADDED EXPORT VIEWS FOR PATIENTS / PROVIDERS / VISITS ==========


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_patients_csv(request):
    from patients.models import Patient
    records = Patient.objects.all()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="patients.csv"'
    writer = csv.writer(response)
    writer.writerow(['first_name', 'last_name', 'dob', 'gender', 'insurance_id', 'payer'])
    for obj in records:
        writer.writerow([str(obj.first_name), str(obj.last_name), str(obj.dob), str(obj.gender), str(obj.insurance_id), str(obj.payer)])
    return response



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_patients_pdf(request):
    from patients.models import Patient
    records = Patient.objects.all()
    html_string = render_to_string('patients_pdf.html', {'patients': records})
    pdf_file = HTML(string=html_string).write_pdf()
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="patients.pdf"'
    return response



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_patients_zip(request):
    from patients.models import Patient
    records = Patient.objects.all()
    buffer = BytesIO()
    zip_file = ZipFile(buffer, 'w')

    # CSV part
    csv_io = TextIOWrapper(BytesIO(), encoding='utf-8', newline='')
    writer = csv.writer(csv_io)
    writer.writerow(['first_name', 'last_name', 'dob', 'gender', 'insurance_id', 'payer'])
    for obj in records:
        writer.writerow([str(obj.first_name), str(obj.last_name), str(obj.dob), str(obj.gender), str(obj.insurance_id), str(obj.payer)])
    csv_io.seek(0)
    zip_file.writestr("patients.csv", csv_io.read())

    # PDF part
    html_string = render_to_string('patients_pdf.html', {'patients': records})
    pdf_file = HTML(string=html_string).write_pdf()
    zip_file.writestr("patients.pdf", pdf_file)

    zip_file.close()
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename="patients.zip"'
    return response



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_providers_csv(request):
    from providers.models import Provider
    records = Provider.objects.all()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="providers.csv"'
    writer = csv.writer(response)
    writer.writerow(['provider_name', 'npi', 'certification', 'compliance_status'])
    for obj in records:
        writer.writerow([str(obj.provider_name), str(obj.npi), str(obj.certification), str(obj.compliance_status)])
    return response



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_providers_pdf(request):
    from providers.models import Provider
    records = Provider.objects.all()
    html_string = render_to_string('providers_pdf.html', {'providers': records})
    pdf_file = HTML(string=html_string).write_pdf()
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="providers.pdf"'
    return response



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_providers_zip(request):
    from providers.models import Provider
    records = Provider.objects.all()
    buffer = BytesIO()
    zip_file = ZipFile(buffer, 'w')

    # CSV part
    csv_io = TextIOWrapper(BytesIO(), encoding='utf-8', newline='')
    writer = csv.writer(csv_io)
    writer.writerow(['provider_name', 'npi', 'certification', 'compliance_status'])
    for obj in records:
        writer.writerow([str(obj.provider_name), str(obj.npi), str(obj.certification), str(obj.compliance_status)])
    csv_io.seek(0)
    zip_file.writestr("providers.csv", csv_io.read())

    # PDF part
    html_string = render_to_string('providers_pdf.html', {'providers': records})
    pdf_file = HTML(string=html_string).write_pdf()
    zip_file.writestr("providers.pdf", pdf_file)

    zip_file.close()
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename="providers.zip"'
    return response



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_visits_csv(request):
    from visits.models import Visit
    records = Visit.objects.all()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="visits.csv"'
    writer = csv.writer(response)
    writer.writerow(['patient', 'provider', 'visit_date', 'duration', 'status'])
    for obj in records:
        writer.writerow([str(obj.patient), str(obj.provider), str(obj.visit_date), str(obj.duration), str(obj.status)])
    return response



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_visits_pdf(request):
    from visits.models import Visit
    records = Visit.objects.all()
    html_string = render_to_string('visits_pdf.html', {'visits': records})
    pdf_file = HTML(string=html_string).write_pdf()
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="visits.pdf"'
    return response



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_visits_zip(request):
    from visits.models import Visit
    records = Visit.objects.all()
    buffer = BytesIO()
    zip_file = ZipFile(buffer, 'w')

    # CSV part
    csv_io = TextIOWrapper(BytesIO(), encoding='utf-8', newline='')
    writer = csv.writer(csv_io)
    writer.writerow(['patient', 'provider', 'visit_date', 'duration', 'status'])
    for obj in records:
        writer.writerow([str(obj.patient), str(obj.provider), str(obj.visit_date), str(obj.duration), str(obj.status)])
    csv_io.seek(0)
    zip_file.writestr("visits.csv", csv_io.read())

    # PDF part
    html_string = render_to_string('visits_pdf.html', {'visits': records})
    pdf_file = HTML(string=html_string).write_pdf()
    zip_file.writestr("visits.pdf", pdf_file)

    zip_file.close()
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename="visits.zip"'
    return response
