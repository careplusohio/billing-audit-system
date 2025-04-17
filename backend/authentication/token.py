from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.models import User
from rest_framework import serializers

class UsernameOrEmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        login = attrs.get("username")  # this field holds either username or email
        password = attrs.get("password")

        # First, try login as username
        try:
            user = User.objects.get(username=login)
        except User.DoesNotExist:
            # Then try login as email
            try:
                user = User.objects.get(email=login)
            except User.DoesNotExist:
                raise serializers.ValidationError("Invalid username or email")

        attrs["username"] = user.username  # required for TokenObtainPairSerializer
        return super().validate(attrs)
