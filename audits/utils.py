from datetime import timedelta
from django.utils.timezone import now


def is_password_expired(user, max_age_days=90):
    try:
        profile = UserProfile.objects.get(user=user)
        return (now() - profile.password_changed_at) > timedelta(days=max_age_days)
    except UserProfile.DoesNotExist:
        return True  # Force password change if no profile exists
def log_action(user, action, details):
    AuditLog.objects.create(
        user=user,
        action=action,
        details=details
    )