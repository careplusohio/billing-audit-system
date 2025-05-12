# /billing-audit-system/authentication/serializers.py

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer



class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        if self.user.is_superuser:
            data['role'] = "admin"
        else:
            data['role'] = "auditor"
        return data
