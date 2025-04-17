from django.contrib import admin
from .models import BillingRecord, AuditResult, Patient, Provider, ComplianceRule

admin.site.register(BillingRecord)
admin.site.register(AuditResult)
admin.site.register(Patient)
admin.site.register(Provider)
admin.site.register(ComplianceRule)
