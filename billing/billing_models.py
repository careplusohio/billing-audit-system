# /biling-audit-system/billing/models.py
from django.db import models

class Patient(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    dob = models.DateField()
    gender = models.CharField(max_length=10)
    insurance_id = models.CharField(max_length=20)
    payer = models.CharField(max_length=100)

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
    payer = models.CharField(max_length=100)
    service_date = models.DateField()
    service_code = models.CharField(max_length=20)
    diagnosis_code = models.CharField(max_length=20)
    units = models.IntegerField()
    amount_billed = models.DecimalField(max_digits=10, decimal_places=2)
    allowed_amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2)
    billing_status = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.patient} - {self.service_code} - {self.service_date}"
