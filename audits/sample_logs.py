import os
import sys
import django

# 👇 ADD THIS: Include the path to the parent directory so 'backend' can be found
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()

from audits.models import AuditActivityLog
from django.contrib.auth import get_user_model

User = get_user_model()

# Fetch the 'abdihakim' user instance
try:
    user = User.objects.get(username='abdihakim')
except User.DoesNotExist:
    raise ValueError("User 'abdihakim' does not exist. Please create this user before running the script.")

# Create sample logs
logs = [
    AuditActivityLog(user=user, action_type='Login', description='Admin logged in successfully'),
    AuditActivityLog(user=user, action_type='View', description='Admin viewed a patient record'),
    AuditActivityLog(user=user, action_type='Export', description='Admin exported audit logs'),
    AuditActivityLog(user=user, action_type='Edit', description='Admin updated a provider record'),
    AuditActivityLog(user=user, action_type='Delete', description='Admin deleted a patient record'),
]

# Bulk insert logs
AuditActivityLog.objects.bulk_create(logs)

print("✅ Sample audit logs created successfully!")
