from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()


class Patient(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10)
    dob = models.DateField()
    insurance_id = models.CharField(max_length=50)
    payer = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='patient_photos/', null=True, blank=True)  # ✅ NEW FIELD

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Provider(models.Model):
    provider_name = models.CharField(max_length=100)
    npi = models.CharField(max_length=20)
    certification = models.CharField(max_length=100)
    compliance_status = models.CharField(max_length=50)

    def __str__(self):
        return self.provider_name

class BillingRecord(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE)
    payer = models.CharField(max_length=50)
    service_date = models.DateField()
    service_code = models.CharField(max_length=20)
    diagnosis_code = models.CharField(max_length=20)
    units = models.IntegerField()
    amount_billed = models.DecimalField(max_digits=10, decimal_places=2)
    allowed_amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2)
    billing_status = models.CharField(max_length=20, default="Submitted")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient} - {self.service_code} - {self.service_date}"

class AuditLog(models.Model):
    STATUS_CHOICES = [
        ("open", "Open"),
        ("resolved", "Resolved"),
        ("other", "Other"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action_type = models.CharField(max_length=20)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="open")
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.action_type}"
