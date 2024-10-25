from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from ..models import Service
from ..serializers.service_serializer import ServiceSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def service_list(request):
    services = Service.objects.filter(is_active=True)
    serializer = ServiceSerializer(services, many=True)
    return Response(serializer.data)
