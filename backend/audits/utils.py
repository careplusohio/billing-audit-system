from datetime import timedelta
from django.utils.timezone import now
from .models import UserProfile

def is_password_expired(user, max_age_days=90):
    try:
        profile = UserProfile.objects.get(user=user)
        return (now() - profile.password_changed_at) > timedelta(days=max_age_days)
    except UserProfile.DoesNotExist:
        return True  # Force password change if no profile exists
