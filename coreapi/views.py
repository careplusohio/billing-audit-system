from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

@api_view(["GET"])
def coreapi_ping(request):
    return Response({"message": "CoreAPI is working ✅"})

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_info(request):
    user = request.user
    return Response({
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "role": getattr(user, "role", "unknown")
    })
