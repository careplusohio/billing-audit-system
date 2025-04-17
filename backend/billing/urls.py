from django.urls import path
from .views import billing_records  # ✅ This should exist in views.py

urlpatterns = [
    path('billing-records/', billing_records),
]
