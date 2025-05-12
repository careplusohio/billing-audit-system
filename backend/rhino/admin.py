# File: backend/rhino/admin.py
from django.contrib import admin
from .models import RhinoClaim

@admin.register(RhinoClaim)
class RhinoClaimAdmin(admin.ModelAdmin):
    list_display = [
        'rb_claim_id', 'patient_first_name', 'patient_last_name', 'payer', 'claim_status',
        'date_of_service', 'total_billed', 'total_paid', 'paycheck_date'
    ]
    search_fields = ['rb_claim_id', 'patient_first_name', 'patient_last_name', 'payer']
    list_filter = ['claim_status', 'paycheck_date']
