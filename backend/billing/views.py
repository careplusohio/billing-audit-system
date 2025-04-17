from django.http import JsonResponse

def billing_records(request):
    return JsonResponse({"message": "Billing records endpoint is working!"})
