from django.http import JsonResponse

def providers_list(request):
    return JsonResponse({"message": "✅ Providers endpoint is working"})
