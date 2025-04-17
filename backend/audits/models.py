from django.db import models
from django.contrib.auth.models import User
import uuid

# ✅ Added to support password expiration tracking
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    password_changed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} profile"

# ✅ Existing models
class Patient(models.Model):
    patient_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    dob = models.DateField()
    gender = models.CharField(max_length=10)
    insurance_id = models.CharField(max_length=100)
    payer = models.CharField(max_length=100)

class Provider(models.Model):
    provider_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    provider_name = models.CharField(max_length=255)
    npi = models.CharField(max_length=50)
    certification = models.CharField(max_length=255)
    compliance_status = models.CharField(max_length=50)

class BillingRecord(models.Model):
    record_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    provider = models.ForeignKey(Provider, on_delete=models.SET_NULL, null=True)
    payer = models.CharField(max_length=100)
    service_date = models.DateField()
    service_code = models.CharField(max_length=20)
    diagnosis_code = models.CharField(max_length=20)
    units = models.IntegerField()
    amount_billed = models.DecimalField(max_digits=10, decimal_places=2)
    allowed_amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2)
    billing_status = models.CharField(max_length=50)
    import_date = models.DateTimeField(auto_now_add=True)

class AuditResult(models.Model):
    audit_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    billing_record = models.ForeignKey(BillingRecord, on_delete=models.CASCADE)
    issue_type = models.CharField(max_length=100)
    description = models.TextField()
    status = models.CharField(max_length=50, default='Open')
    auditor_comments = models.TextField(blank=True, null=True)
    review_date = models.DateTimeField(auto_now=True)

class ComplianceRule(models.Model):
    rule_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    payer = models.CharField(max_length=100)
    rule_description = models.TextField()
    code_type = models.CharField(max_length=50)
    active = models.BooleanField(default=True)

class AuditLog(models.Model):
    ACTION_TYPES = [
        ("ROLE_CHANGED", "Role Changed"),
        ("PASSWORD_RESET", "Password Reset"),
        ("CSV_UPLOAD", "CSV Upload"),
        ("LOGIN", "Login"),
        ("LOGOUT", "Logout"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action_type = models.CharField(max_length=50, choices=ACTION_TYPES)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.action_type} @ {self.timestamp}"