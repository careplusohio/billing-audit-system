from django.http import JsonResponse
from .models import Patient

def patients_list(request):
    patients = Patient.objects.all()
    data = []
    for patient in patients:
        data.append({
            "id": patient.id,
            "first_name": patient.first_name,
            "last_name": patient.last_name,
            # add more fields if you want
        })
    return JsonResponse(data, safe=False)
