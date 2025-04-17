from django.contrib.auth.models import User
from rest_framework import serializers, generics, filters, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.views import APIView
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.conf import settings
import csv
from io import TextIOWrapper
from weasyprint import HTML
from .models import BillingRecord, Patient, Provider, AuditResult
from .serializers import (
    BillingRecordSerializer,
    PatientSerializer,
    ProviderSerializer,
    AuditResultSerializer,
)
from .permissions import IsAdminUserFromJWT, RequireFreshPassword
from .models import AuditLog  # ✅ for logging actions

# ========== Dashboard Summary ==========
@api_view(['GET'])
def audit_summary_stats(request):
    total_records = BillingRecord.objects.count()
    total_issues = AuditResult.objects.count()
    open_issues = AuditResult.objects.filter(status='Open').count()
    resolved_issues = AuditResult.objects.filter(status='Resolved').count()

    return Response({
        "total_records": total_records,
        "total_issues": total_issues,
        "open_issues": open_issues,
        "resolved_issues": resolved_issues
    })


# ========== User Invitation ==========
@api_view(['POST'])
@permission_classes([IsAdminUserFromJWT])
def invite_user(request):
    email = request.data.get("email")
    username = request.data.get("username")

    if not email or not username:
        return Response({"error": "Username and email are required."}, status=400)

    if User.objects.filter(username=username).exists():
        return Response({"error": "Username already exists."}, status=400)

    temp_password = get_random_string(length=10)
    user = User.objects.create_user(username=username, email=email, password=temp_password)
    user.is_active = True
    user.save()

    send_mail(
        subject="You've been invited to CarePlus Audit System",
        message=f"Your login credentials:\nUsername: {username}\nPassword: {temp_password}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )

    return Response({"message": "User invited successfully.", "temp_password": temp_password})

@api_view(['GET'])
@permission_classes([IsAdminUserFromJWT])
def export_audit_logs_csv(request):
    start_date = request.GET.get('start')
    end_date = request.GET.get('end')

    logs = AuditLog.objects.select_related("user")

    if start_date and end_date:
        logs = logs.filter(timestamp__range=[start_date, end_date])

    logs = logs.order_by('-timestamp')
    
from weasyprint import HTML


    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="audit_logs.csv"'

    writer = csv.writer(response)
    writer.writerow(['User', 'Action Type', 'Description', 'Timestamp'])

    for log in logs:
        writer.writerow([
            log.user.username,
            log.action_type,
            log.description,
            log.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        ])

    return response

# ========== Password Change ==========
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    user = request.user
    current_password = request.data.get("current_password")
    new_password = request.data.get("new_password")

    if not user.check_password(current_password):
        return Response({"error": "Current password is incorrect."}, status=400)

    user.set_password(new_password)
    user.save()

    return Response({"message": "Password updated successfully."})


# ========== File Upload + Audit ==========
class BillingCSVUploadView(APIView):
    permission_classes = [IsAdminUserFromJWT]
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
                    defaults={
                        "dob": "1990-01-01",
                        "gender": "Other",
                        "insurance_id": "000",
                        "payer": row["payer"]
                    }
                )

                provider, _ = Provider.objects.get_or_create(
                    provider_name=row["provider_name"],
                    defaults={
                        "npi": "0000",
                        "certification": "Test",
                        "compliance_status": "Active"
                    }
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

                # === Audit Rules ===
                if not record.service_code:
                    AuditResult.objects.create(
                        billing_record=record,
                        issue_type="Missing Service Code",
                        description="Service code is missing from the record.",
                        status="Open"
                    )

                if not record.diagnosis_code:
                    AuditResult.objects.create(
                        billing_record=record,
                        issue_type="Missing Diagnosis Code",
                        description="Diagnosis code is missing from the record.",
                        status="Open"
                    )

                if not record.payer:
                    AuditResult.objects.create(
                        billing_record=record,
                        issue_type="Missing Payer",
                        description="Payer information is missing.",
                        status="Open"
                    )

                if record.units == 0:
                    AuditResult.objects.create(
                        billing_record=record,
                        issue_type="Invalid Units",
                        description="Billed units are zero (0).",
                        status="Open"
                    )

                if record.amount_billed > record.allowed_amount:
                    AuditResult.objects.create(
                        billing_record=record,
                        issue_type="Rate Discrepancy",
                        description="Amount billed exceeds allowed rate.",
                        status="Open"
                    )

                imported += 1

            except Exception as e:
                errors.append(str(e))

        return Response({
            "imported": imported,
            "errors": errors
        }, status=201)


# ========== List Views ==========
class BillingRecordListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, RequireFreshPassword]
    queryset = BillingRecord.objects.all()
    serializer_class = BillingRecordSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['payer', 'service_date', 'billing_status']
    search_fields = ['service_code', 'diagnosis_code', 'payer']
    ordering_fields = ['service_date', 'amount_billed', 'allowed_amount', 'paid_amount']


class PatientListCreateView(generics.ListCreateAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['first_name', 'last_name', 'insurance_id']
    ordering_fields = ['first_name', 'last_name', 'dob']


class ProviderListCreateView(generics.ListCreateAPIView):
    queryset = Provider.objects.all()
    serializer_class = ProviderSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['provider_name', 'npi']


class AuditResultListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdminUserFromJWT, RequireFreshPassword]
    queryset = AuditResult.objects.all()
    serializer_class = AuditResultSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['issue_type', 'status']
    search_fields = ['description']
    ordering_fields = ['review_date']


# ========== User Management ==========
class UserListSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()

    def get_role(self, obj):
        return "admin" if obj.is_superuser else "auditor"

    class Meta:
        model = User
        fields = ["id", "username", "email", "is_active", "role", "is_superuser"]


class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserListSerializer
    permission_classes = [IsAuthenticated]


@api_view(['POST'])
@permission_classes([IsAdminUserFromJWT])
def toggle_user_role(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        user.is_superuser = not user.is_superuser
        user.save()
        return Response({
            "message": "Role updated successfully.",
            "new_role": "admin" if user.is_superuser else "auditor"
        })
    except User.DoesNotExist:
        return Response({"error": "User not found."}, status=404)

AuditLog.objects.create(
    user=request.user,
    action_type="ROLE_CHANGED",
    description=f"{request.user.username} changed role of {user.username} to {'admin' if user.is_superuser else 'auditor'}"
)
AuditLog.objects.create(
    user=request.user,
    action_type="PASSWORD_RESET",
    description="User changed their password"
)
AuditLog.objects.create(
    user=request.user,
    action_type="CSV_UPLOAD",
    description=f"{imported} records uploaded from CSV"
)
AuditLog.objects.create(
    user=request.user,
    action_type="ROLE_CHANGED",
    description=f"{request.user.username} changed role of {user.username} to {'admin' if user.is_superuser else 'auditor'}"
)
AuditLog.objects.create(
    user=request.user,
    action_type="CSV_UPLOAD",
    description=f"{imported} billing records uploaded from CSV by {request.user.username}"
)

# ========== Test Endpoint ==========
@csrf_exempt
def audit_results(request):
    return JsonResponse({"message": "✅ Audit results endpoint is working"})

class AuditLogListView(generics.ListAPIView):
    queryset = AuditLog.objects.all().order_by('-timestamp')
    serializer_class = AuditLogSerializer
    permission_classes = [IsAdminUserFromJWT]
