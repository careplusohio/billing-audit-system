import os
import sys
import django
import random
from datetime import datetime, timedelta

# Setup Django environment
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/../'))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()

from billing.models import Patient, Provider, BillingRecord

# --- Create sample patients if none exist ---
if not Patient.objects.exists():
    for i in range(5):
        Patient.objects.create(
            first_name=f"John{i}",
            last_name=f"Doe{i}",
            dob="1980-01-01",
            gender="Male",
            insurance_id=f"INS{i}",
            payer="Medicare"
        )
    print("✅ Sample patients created.")

# --- Create sample providers if none exist ---
if not Provider.objects.exists():
    for i in range(3):
        Provider.objects.create(
            provider_name=f"Provider{i}",
            npi=f"NPI{i}",
            certification="Certified",
            compliance_status="Compliant"
        )
    print("✅ Sample providers created.")

patients = list(Patient.objects.all())
providers = list(Provider.objects.all())

# --- Create sample billing records ---
for i in range(10):
    BillingRecord.objects.create(
        patient=random.choice(patients),
        provider=random.choice(providers),
        payer="Medicare",
        service_date=datetime.today() - timedelta(days=random.randint(1, 90)),
        service_code=f"SVC{i}",
        diagnosis_code=f"DIA{i}",
        units=random.randint(1, 5),
        amount_billed=round(random.uniform(100, 1000), 2),
        allowed_amount=round(random.uniform(50, 800), 2),
        paid_amount=round(random.uniform(30, 700), 2),
        billing_status=random.choice(["Pending", "Paid", "Denied"])
    )

print("✅ Sample billing records created.")
