from django.contrib import admin
from .models import AuditResult
from billing.models import AuditLog
admin.site.register(AuditResult)

