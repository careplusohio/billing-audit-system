# File: billing-audit-system/backend/rhino/models.py
from django.db import models

class RhinoClaim(models.Model):
    patient_first_name = models.CharField(max_length=255)
    patient_last_name = models.CharField(max_length=255)
    patient_dob = models.DateField(null=True, blank=True)
    total_billed = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_paid = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    payer = models.CharField(max_length=255, null=True, blank=True)
    claim_status = models.CharField(max_length=255, null=True, blank=True)

    # ✅ Newly added fields for RhinoCSVUploadView
    trading_partner_name = models.CharField(max_length=255, null=True, blank=True)
    patient_control_number = models.CharField(max_length=255, null=True, blank=True)
    total_claim_charge_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.patient_first_name} {self.patient_last_name} - {self.claim_status}"
