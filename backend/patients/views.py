from django.http import JsonResponse

def patients_list(request):
    return JsonResponse({"message": "✅ Patients endpoint is working"})
