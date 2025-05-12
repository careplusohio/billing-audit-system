# /backend/authentication/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ("admin", "Admin"),
        ("auditor", "Auditor"),
        ("manager", "Manager"),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="auditor")

    def __str__(self):
        return f"{self.username} ({self.role})"
