from django.db import models
from billing.models import BillingRecord
from django.contrib.auth import get_user_model

User = get_user_model()

class AuditResult(models.Model):
    billing_record = models.ForeignKey(BillingRecord, on_delete=models.CASCADE)
    issue_type = models.CharField(max_length=100)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=[("Open", "Open"), ("Resolved", "Resolved")])
    review_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.issue_type} - {self.status}"

class RhinoClaim(models.Model):
    trading_partner_id = models.CharField(max_length=255, null=True, blank=True)
    rb_claim_id = models.CharField(max_length=255, primary_key=True)
    edi_file_id = models.CharField(max_length=255, null=True, blank=True)
    edi_file_name = models.CharField(max_length=255, null=True, blank=True)
    provider_name = models.CharField(max_length=255, null=True, blank=True)
    payer_provider_id = models.CharField(max_length=255, null=True, blank=True)
    provider_npi = models.CharField(max_length=255, null=True, blank=True)
    patient_first_name = models.CharField(max_length=255, null=True, blank=True)
    patient_last_name = models.CharField(max_length=255, null=True, blank=True)
    patient_dob = models.DateField(null=True, blank=True)
    patient_payer_id = models.CharField(max_length=255, null=True, blank=True)
    date_of_service = models.DateField(null=True, blank=True)
    total_charges = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    claim_status = models.CharField(max_length=255, null=True, blank=True)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    denial_reason = models.TextField(null=True, blank=True)

    # Additional fields for exports & dashboard
    original_claim_id = models.CharField(max_length=255, blank=True, null=True)
    adjustment_claim_id = models.CharField(max_length=255, blank=True, null=True)
    icn = models.CharField(max_length=255, blank=True, null=True)
    payer = models.CharField(max_length=255, blank=True, null=True)
    payer_type = models.CharField(max_length=255, blank=True, null=True)
    procedure_code = models.CharField(max_length=255, blank=True, null=True)
    created_date = models.DateField(blank=True, null=True)
    service_begin_date = models.DateField(blank=True, null=True)
    service_end_date = models.DateField(blank=True, null=True)
    total_hours = models.FloatField(blank=True, null=True)
    total_units = models.IntegerField(blank=True, null=True)
    patient_responsibility = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total_billed = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total_paid = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    paycheck_date = models.DateField(blank=True, null=True)
    patient_sex = models.CharField(max_length=10, blank=True, null=True)
    patient_address_1 = models.CharField(max_length=255, blank=True, null=True)
    patient_address_2 = models.CharField(max_length=255, blank=True, null=True)
    patient_city = models.CharField(max_length=255, blank=True, null=True)
    patient_state = models.CharField(max_length=255, blank=True, null=True)
    patient_zip = models.CharField(max_length=20, blank=True, null=True)
    prior_authorization = models.CharField(max_length=255, blank=True, null=True)
    discharge_date = models.DateField(blank=True, null=True)
    diagnosis_1 = models.CharField(max_length=255, blank=True, null=True)
    diagnosis_2 = models.CharField(max_length=255, blank=True, null=True)
    diagnosis_3 = models.CharField(max_length=255, blank=True, null=True)
    diagnosis_4 = models.CharField(max_length=255, blank=True, null=True)
    orp_first_name = models.CharField(max_length=255, blank=True, null=True)
    orp_last_name = models.CharField(max_length=255, blank=True, null=True)
    orp_npi = models.CharField(max_length=255, blank=True, null=True)
    accident_type = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = "audits_rhino_claim"
        managed = True

    def __str__(self):
        return f"{self.patient_first_name} {self.patient_last_name} ({self.date_of_service})"

class AuditActivityLog(models.Model):
    ACTION_TYPES = [
        ('VIEW', 'View'),
        ('EXPORT', 'Export'),
        ('STATUS_CHANGE', 'Status Change'),
        ('DELETE', 'Delete'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action_type = models.CharField(max_length=50, choices=ACTION_TYPES)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.action_type} at {self.timestamp}"

class AuditIssueHistory(models.Model):
    audit_issue = models.ForeignKey(AuditResult, on_delete=models.CASCADE)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    previous_status = models.CharField(max_length=20, blank=True, null=True)
    new_status = models.CharField(max_length=20, blank=True, null=True)
    change_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Audit Issue {self.audit_issue.id} changed to {self.new_status} by {self.changed_by}"

class AuditIssue(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action_type = models.CharField(max_length=100)
    description = models.TextField()
    status = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Issue: {self.action_type} ({self.status})"
