from rest_framework import serializers
from billing.models import BillingRecord, Patient, Provider
from .models import AuditResult, RhinoClaim  # ✅ RhinoClaim imported
from .models import AuditActivityLog, AuditIssue  # ✅ also import AuditIssue
from billing.models import AuditLog
from django.contrib.auth import get_user_model

User = get_user_model()
# ------------------ AUDIT LOG ------------------
class AuditLogSerializer(serializers.ModelSerializer):
    user_email = serializers.SerializerMethodField()

    class Meta:
        model = AuditLog
        fields = ['id', 'user_email', 'action_type', 'description', 'status', 'timestamp']

    def get_user_email(self, obj):
        return obj.user.email if obj.user else "Unknown"

# ------------------ AUDIT ACTIVITY LOG ------------------

class AuditActivityLogSerializer(serializers.ModelSerializer):
    user_email = serializers.SerializerMethodField()

    class Meta:
        model = AuditActivityLog
        fields = ['id', 'user_email', 'action_type', 'description', 'timestamp']

    def get_user_email(self, obj):
        return obj.user.email if obj.user else "Unknown"

# ------------------ BILLING RECORD ------------------

class BillingRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillingRecord
        fields = '__all__'

# ------------------ PATIENT ------------------

class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = '__all__'

# ------------------ PROVIDER ------------------

class ProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Provider
        fields = '__all__'

# ------------------ AUDIT RESULT ------------------

class AuditResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditResult
        fields = '__all__'

# ------------------ RHINO CLAIM ------------------

class RhinoClaimSerializer(serializers.ModelSerializer):
    class Meta:
        model = RhinoClaim
        fields = '__all__'

# ------------------ AUDIT ISSUE ------------------

class AuditIssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditIssue
        fields = '__all__'

