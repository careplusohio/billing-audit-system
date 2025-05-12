from django.db import models
from patients.models import Patient
from providers.models import Provider  # or wherever your provider model is

class Visit(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE)
    visit_date = models.DateField()
    visit_time = models.TimeField()
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.visit_date} - {self.patient} with {self.provider}"
