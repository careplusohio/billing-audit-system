import os
import sys   # 🔥 You forgot this line
import django

# Fix the Python path so it can find the 'backend' module
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/../'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from audits.models import AuditIssue, AuditActivityLog
from django.contrib.auth import get_user_model
from django.utils import timezone


User = get_user_model()

# Get the first available user (or your superuser ID)
user = User.objects.first()

if not user:
    raise Exception("No user found. Please create a user first.")

# ------------------------
# Seed Audit Issues
# ------------------------
if not AuditIssue.objects.exists():
    AuditIssue.objects.bulk_create([
        AuditIssue(user=user, action_type="View", description="Viewed patient record", status="open"),
        AuditIssue(user=user, action_type="Edit", description="Edited provider details", status="open"),
        AuditIssue(user=user, action_type="Delete", description="Deleted billing record", status="resolved"),
        AuditIssue(user=user, action_type="Export", description="Exported audit logs", status="resolved"),
        AuditIssue(user=user, action_type="Login", description="Logged in successfully", status="open"),
    ])
    print("Sample Audit Issues created.")
else:
    print("Audit Issues already exist.")

# ------------------------
# Seed Activity Logs
# ------------------------
if not AuditActivityLog.objects.exists():
    AuditActivityLog.objects.bulk_create([
        AuditActivityLog(user=user, action_type="Login", description="Admin logged in"),
        AuditActivityLog(user=user, action_type="View", description="Viewed patient data"),
        AuditActivityLog(user=user, action_type="Edit", description="Updated provider information"),
        AuditActivityLog(user=user, action_type="Delete", description="Removed billing entry"),
        AuditActivityLog(user=user, action_type="Export", description="Exported data to CSV"),
    ])
    print("Sample Activity Logs created.")
else:
    print("Activity Logs already exist.")
