from django.db import models

class Provider(models.Model):
    provider_name = models.CharField(max_length=100)
    npi = models.CharField(max_length=50)
    compliance_status = models.CharField(max_length=100)
    certification = models.CharField(max_length=100)

    def __str__(self):
        return self.provider_name
